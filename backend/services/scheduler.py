"""
Background Job Scheduler - Runs scans and sends daily Telegram reports
"""
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import logging

logger = logging.getLogger(__name__)

# Tier scan frequencies (hours between scans)
TIER_SCAN_FREQUENCY = {
    "free": 24,      # Once per day
    "sniper": 12,    # Twice per day
    "elite": 6,      # 4 times per day
    "agency": 4,     # 6 times per day
    "enterprise": 2  # 12 times per day
}

EASTERN_TZ = pytz.timezone('US/Eastern')


class ScanScheduler:
    def __init__(self, db):
        self.db = db
        self.scheduler = AsyncIOScheduler(timezone=EASTERN_TZ)
        self._running = False

    def start(self):
        """Start the scheduler"""
        if self._running:
            return

        # Daily report job at 7 AM Eastern
        self.scheduler.add_job(
            self.send_daily_reports,
            CronTrigger(hour=7, minute=0, timezone=EASTERN_TZ),
            id='daily_telegram_report',
            replace_existing=True
        )

        # Background scan job - runs every hour, checks which users need scans
        self.scheduler.add_job(
            self.run_scheduled_scans,
            CronTrigger(minute=0, timezone=EASTERN_TZ),
            id='hourly_scan_check',
            replace_existing=True
        )

        # Archive old products daily at 6:55 AM (before report)
        self.scheduler.add_job(
            self.archive_daily_products,
            CronTrigger(hour=6, minute=55, timezone=EASTERN_TZ),
            id='archive_products',
            replace_existing=True
        )

        self.scheduler.start()
        self._running = True
        logger.info("Scheduler started - Daily reports at 7 AM Eastern")

    def stop(self):
        """Stop the scheduler"""
        if self._running:
            self.scheduler.shutdown()
            self._running = False

    async def run_scheduled_scans(self):
        """Check and run scans for users based on their tier frequency"""
        logger.info("Running scheduled scan check...")

        users = await self.db.users.find(
            {"openai_api_key": {"$ne": None}},
            {"_id": 0, "id": 1, "email": 1, "subscription_tier": 1, "openai_api_key": 1, "last_scan_at": 1}
        ).to_list(1000)

        now = datetime.now(timezone.utc)

        for user in users:
            tier = user.get("subscription_tier", "free")
            frequency_hours = TIER_SCAN_FREQUENCY.get(tier, 24)
            last_scan = user.get("last_scan_at")

            # Check if scan is due
            should_scan = False
            if not last_scan:
                should_scan = True
            else:
                if isinstance(last_scan, str):
                    last_scan = datetime.fromisoformat(last_scan.replace('Z', '+00:00'))
                hours_since_scan = (now - last_scan).total_seconds() / 3600
                should_scan = hours_since_scan >= frequency_hours

            if should_scan:
                await self.run_user_scan(user)

    async def run_user_scan(self, user: Dict[str, Any]):
        """Run AI scan for a specific user"""
        from services.ai_scanner import create_scanner

        user_id = user["id"]
        openai_key = user.get("openai_api_key")

        if not openai_key:
            logger.warning(f"Skipping scan for user {user_id} - no OpenAI API key")
            return

        logger.info(f"Running scan for user {user_id} ({user.get('email')})")

        try:
            scanner = create_scanner(openai_key)
            user_doc = await self.db.users.find_one({"id": user_id}, {"_id": 0, "filters": 1})
            filters = user_doc.get("filters", {}) if user_doc else {}
            results = await scanner.run_full_scan(filters)

            # Store scan results
            scan_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            scan_record = {
                "user_id": user_id,
                "scan_date": scan_date,
                "scan_type": "scheduled",
                "results_summary": {
                    "total_products": results.get("count", 0),
                    "source_stats": results.get("source_stats", {}),
                    "raw_products_scraped": results.get("raw_products_scraped", 0),
                },
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await self.db.scan_history.insert_one(scan_record)

            # Update user's last scan time
            await self.db.users.update_one(
                {"id": user_id},
                {"$set": {"last_scan_at": datetime.now(timezone.utc).isoformat()}}
            )

            # Process and store discovered products
            await self._process_scan_results(user_id, scan_date, results)

            logger.info(f"Scan complete for user {user_id} - {results.get('count', 0)} products found")

        except Exception as e:
            logger.error(f"Scan failed for user {user_id}: {e}")

    async def _process_scan_results(self, user_id: str, scan_date: str, results: Dict):
        """Process scan results and store as daily products for this user"""
        import uuid

        products = results.get("products", [])
        if not products:
            return

        # Sort by overall_score or trend_score and take top 10
        products.sort(key=lambda x: x.get("overall_score", x.get("trend_score", 0)), reverse=True)
        top_products = products[:10]

        # Store as daily products for this specific user
        for product in top_products:
            product_doc = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "scan_date": scan_date,
                "name": product.get("name", "Unknown"),
                "source": product.get("source", "unknown"),
                "overall_score": product.get("overall_score", product.get("trend_score", 0)),
                "trend_score": product.get("trend_score", 0),
                "trend_data": product.get("trend_data", {}),
                "source_cost": product.get("source_cost", 0),
                "recommended_price": product.get("recommended_price", 0),
                "margin_percent": product.get("margin_percent", 0),
                "category": product.get("category", "General"),
                "why_trending": product.get("why_trending", ""),
                "saturation_level": product.get("saturation_level", "medium"),
                "active_fb_ads": product.get("active_fb_ads", 0),
                "trend_direction": product.get("trend_direction", "stable"),
                "estimated_views": product.get("estimated_views", 0),
                "is_active": True,
                "discovered_at": datetime.now(timezone.utc).isoformat(),
            }
            await self.db.daily_products.insert_one(product_doc)

    async def archive_daily_products(self):
        """Archive yesterday's products before new scan"""
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

        result = await self.db.daily_products.update_many(
            {"scan_date": yesterday, "is_active": True},
            {"$set": {"is_active": False, "archived_at": datetime.now(timezone.utc).isoformat()}}
        )
        logger.info(f"Archived {result.modified_count} products from {yesterday}")

    async def send_daily_reports(self):
        """Send daily Telegram reports to all configured users"""
        logger.info("Sending daily Telegram reports...")

        # Get users with Telegram configured
        users = await self.db.users.find(
            {
                "telegram_bot_token": {"$ne": None},
                "telegram_chat_id": {"$ne": None}
            },
            {"_id": 0}
        ).to_list(1000)

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        sent_count = 0

        for user in users:
            try:
                # Check notification preferences
                prefs = user.get("notification_preferences", {})
                if prefs.get("daily_report") is False:
                    logger.info(f"Skipping daily report for {user.get('email')} - disabled in preferences")
                    continue
                success = await self._send_user_report(user, today)
                if success:
                    sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send report to {user.get('email')}: {e}")

        logger.info(f"Daily reports sent to {sent_count}/{len(users)} users")

    async def _send_user_report(self, user: Dict, scan_date: str) -> bool:
        """Send daily report to a single user with real stats"""
        from services.telegram_bot import TelegramBot

        user_id = user["id"]

        # Get today's products for THIS user first, then fall back to global
        products = await self.db.daily_products.find(
            {"user_id": user_id, "scan_date": scan_date, "is_active": True},
            {"_id": 0}
        ).sort("overall_score", -1).limit(5).to_list(5)

        if not products:
            # Fallback to any active products for this user
            products = await self.db.daily_products.find(
                {"user_id": user_id, "is_active": True},
                {"_id": 0}
            ).sort("overall_score", -1).limit(5).to_list(5)

        if not products:
            # Final fallback to seed products
            products = await self.db.products.find(
                {}, {"_id": 0}
            ).sort("overall_score", -1).limit(5).to_list(5)

        if not products:
            logger.info(f"No products to report for user {user_id}")
            return False

        # Get REAL scan stats from scan_history
        total_scanned = await self.db.scan_history.count_documents({"user_id": user_id})
        today_scans = await self.db.scan_history.count_documents(
            {"user_id": user_id, "scan_date": scan_date}
        )
        total_daily_products = await self.db.daily_products.count_documents(
            {"user_id": user_id, "scan_date": scan_date}
        )

        # Build report with real data
        report_data = {
            "products_scanned": total_daily_products,
            "passed_filters": len(products),
            "fully_validated": len(products),
            "ready_to_launch": len(products),
            "top_products": [
                {
                    "name": p.get("name", "Unknown"),
                    "score": p.get("overall_score", p.get("trend_score", 0)),
                    "source_cost": p.get("source_cost", 0),
                    "sell_price": p.get("recommended_price", 0),
                    "margin": p.get("margin_percent", 0),
                    "fb_ads": p.get("active_fb_ads", 0),
                    "trend_direction": p.get("trend_direction", "up"),
                    "trend_percent": p.get("trend_score", 0),
                }
                for p in products
            ],
            "alerts": [],
        }

        # Send via user's own bot
        bot = TelegramBot()
        bot.bot_token = user["telegram_bot_token"]
        bot.is_configured = True
        bot.base_url = f"https://api.telegram.org/bot{user['telegram_bot_token']}"

        result = await bot.send_daily_report(user["telegram_chat_id"], report_data)

        if result.get("success"):
            logger.info(f"Report sent to {user.get('email')}")
            return True
        else:
            logger.error(f"Failed to send report to {user.get('email')}: {result}")
            return False


# Global scheduler instance
_scheduler = None

def get_scheduler(db) -> ScanScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = ScanScheduler(db)
    return _scheduler

def start_scheduler(db):
    scheduler = get_scheduler(db)
    scheduler.start()
    return scheduler
