"""DropSniper AI - Main FastAPI Application"""
from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
import secrets
from typing import List, Optional

from models import (
    User, UserResponse, Product, LaunchKit, AdCopy, VideoScript,
    DailyReport, ProductBoard, FilterSettings, Supplier
)

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Config - require stable secret to prevent logout on redeploy
JWT_SECRET = os.environ.get('JWT_SECRET')
if not JWT_SECRET:
    logger.warning("JWT_SECRET not set! Generating temporary secret - users will be logged out on restart. Set JWT_SECRET env var for production.")
    JWT_SECRET = secrets.token_hex(32)

# Initialize route dependencies
from routes.deps import init_db, get_current_user, get_db
init_db(db, JWT_SECRET)

# Create app
app = FastAPI(title="DropSniper AI API", version="2.0.0")

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create indexes and start scheduler on startup
@app.on_event("startup")
async def startup_event():
    # Create MongoDB indexes for performance
    try:
        await db.users.create_index("email", unique=True)
        await db.users.create_index("id", unique=True)
        await db.products.create_index("id", unique=True)
        await db.products.create_index([("overall_score", -1)])
        await db.daily_products.create_index([("scan_date", 1), ("is_active", 1)])
        await db.daily_products.create_index([("user_id", 1), ("scan_date", -1)])
        await db.daily_products.create_index([("user_id", 1), ("discovered_at", -1)])
        await db.launch_kits.create_index("user_id")
        await db.launch_kits.create_index("id", unique=True)
        await db.competitors.create_index("user_id")
        await db.scan_history.create_index([("user_id", 1), ("scan_date", -1)])
        await db.boards.create_index("user_id")
        logger.info("MongoDB indexes created")
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")

    # Start background scheduler
    from services.scheduler import start_scheduler
    try:
        start_scheduler(db)
        logger.info("Background scheduler started")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")

# CORS - Use FRONTEND_URL for production, fallback to permissive for dev
FRONTEND_URL = os.environ.get('FRONTEND_URL', '')
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '')

if CORS_ORIGINS:
    origins = [origin.strip() for origin in CORS_ORIGINS.split(',')]
elif FRONTEND_URL:
    origins = [FRONTEND_URL]
    # Also allow common dev origins
    if 'localhost' not in FRONTEND_URL:
        origins.extend(["http://localhost:3000", "http://localhost:3001"])
else:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Admin email
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'jabriel@arisolutionsinc.com')

# Main API router
api_router = APIRouter(prefix="/api")

# Import and include route modules
from routes.auth import router as auth_router
from routes.products import router as products_router
from routes.users import router as users_router
from routes.admin import router as admin_router
from routes.trends import router as trends_router
from routes.export import router as export_router
from routes.payments import router as payments_router
from routes.contact import router as contact_router
from routes.verification import router as verification_router

api_router.include_router(auth_router)
api_router.include_router(products_router)
api_router.include_router(users_router)
api_router.include_router(admin_router)
api_router.include_router(trends_router)
api_router.include_router(export_router)
api_router.include_router(payments_router)
api_router.include_router(contact_router)
api_router.include_router(verification_router)

# ========== LAUNCH KIT ROUTES ==========
@api_router.post("/launch-kit/{product_id}", response_model=LaunchKit)
async def generate_launch_kit(product_id: str, user: User = Depends(get_current_user)):
    check_feature_access(user.subscription_tier, "launch_kit")
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_obj = Product(**product)
    
    launch_kit = LaunchKit(
        product_id=product_id,
        user_id=user.id,
        product_name=product_obj.name,
        product_description=product_obj.description or f"High-quality {product_obj.name} - trending now!",
        ad_copies=[
            AdCopy(style="short", headline=f"🔥 {product_obj.name} - Limited Stock!", body=f"Get yours before it's gone. {int(product_obj.margin_percent)}% OFF today only!", cta="Shop Now"),
            AdCopy(style="long", headline=f"Why Everyone's Talking About {product_obj.name}", body="Join thousands of happy customers. Premium quality at an unbeatable price. Free shipping on orders over $50. 30-day money back guarantee.", cta="Get Yours Today"),
            AdCopy(style="urgency", headline=f"⚡ FLASH SALE: {product_obj.name}", body=f"Only {50} left at this price! Don't miss out on the deal everyone's talking about.", cta="Claim Your Discount"),
        ],
        video_scripts=[
            VideoScript(hook=f"POV: You just discovered {product_obj.name}", problem="You've been searching for the perfect solution...", solution=f"Meet {product_obj.name} - the game changer you need", cta="Link in bio!", duration_seconds=15),
            VideoScript(hook="Wait, you don't have this yet?", problem="Everyone's already using this hack...", solution=f"{product_obj.name} is literally changing lives", cta="Get yours now - link below", duration_seconds=20),
        ],
        target_audiences=[
            f"{product_obj.category} enthusiasts 18-35",
            "Online shoppers interested in trending products",
            "People who engaged with similar product ads",
            f"Lookalike audience from {product_obj.category} buyers"
        ],
        hashtags=[
            "#tiktokmademebuyit", "#viralproduct", "#musthave", "#trending",
            f"#{product_obj.category.lower().replace(' ', '')}", "#shopnow", "#fyp"
        ],
        pricing_tiers={
            "single": product_obj.recommended_price,
            "bundle_2": round(product_obj.recommended_price * 1.8, 2),
            "bundle_3": round(product_obj.recommended_price * 2.5, 2)
        },
        upsell_suggestions=["Extended warranty package", "Premium carrying case", "Bulk discount for 3+"],
        launch_checklist=[
            {"task": "Import product to store", "completed": False},
            {"task": "Set up pricing tiers", "completed": False},
            {"task": "Create product images", "completed": False},
            {"task": "Write SEO description", "completed": False},
            {"task": "Set up Facebook ad campaign", "completed": False},
            {"task": "Create TikTok content", "completed": False},
            {"task": "Contact supplier for samples", "completed": False},
            {"task": "Set up email sequences", "completed": False}
        ],
        status="ready"
    )
    
    doc = launch_kit.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.launch_kits.insert_one(doc)
    
    return launch_kit

@api_router.get("/launch-kits", response_model=List[LaunchKit])
async def get_launch_kits(user: User = Depends(get_current_user)):
    kits = await db.launch_kits.find({"user_id": user.id}, {"_id": 0}).to_list(100)
    return kits

@api_router.get("/launch-kit/{kit_id}", response_model=LaunchKit)
async def get_launch_kit(kit_id: str, user: User = Depends(get_current_user)):
    kit = await db.launch_kits.find_one({"id": kit_id, "user_id": user.id}, {"_id": 0})
    if not kit:
        raise HTTPException(status_code=404, detail="Launch kit not found")
    return kit

# ========== DAILY REPORT ==========
@api_router.get("/reports/daily", response_model=DailyReport)
async def get_daily_report(user: User = Depends(get_current_user)):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report = await db.daily_reports.find_one({"user_id": user.id, "date": today}, {"_id": 0})
    
    if not report:
        # Get real product data for this user
        daily_prods = await db.daily_products.find(
            {"user_id": user.id, "scan_date": today, "is_active": True}, {"_id": 0}
        ).sort("overall_score", -1).limit(5).to_list(5)

        if not daily_prods:
            daily_prods = await db.products.find({}, {"_id": 0}).sort("overall_score", -1).limit(5).to_list(5)

        top_ids = [p.get('id', '') for p in daily_prods]

        # Get real scan stats
        total_scanned = await db.daily_products.count_documents({"user_id": user.id, "scan_date": today})
        total_scans = await db.scan_history.count_documents({"user_id": user.id, "scan_date": today})

        report = DailyReport(
            user_id=user.id,
            date=today,
            products_scanned=total_scanned or len(daily_prods),
            passed_filters=len(daily_prods),
            fully_validated=len(daily_prods),
            ready_to_launch=len(top_ids),
            top_products=top_ids,
            alerts=[]
        )
        doc = report.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.daily_reports.insert_one(doc)
    
    return report

# ========== STATS & SETTINGS ==========
@api_router.get("/stats")
async def get_stats(user: User = Depends(get_current_user)):
    total_products = await db.products.count_documents({})
    total_kits = await db.launch_kits.count_documents({"user_id": user.id})
    total_boards = await db.boards.count_documents({"user_id": user.id})
    
    return {
        "total_products": total_products,
        "total_launch_kits": total_kits,
        "total_boards": total_boards,
        "subscription_tier": user.subscription_tier
    }

@api_router.get("/settings/filters", response_model=FilterSettings)
async def get_filter_settings(user: User = Depends(get_current_user)):
    if user.filters:
        return FilterSettings(**user.filters)
    return FilterSettings()

@api_router.put("/settings/filters", response_model=FilterSettings)
async def update_filter_settings(filters: FilterSettings, user: User = Depends(get_current_user)):
    await db.users.update_one({"id": user.id}, {"$set": {"filters": filters.model_dump()}})
    return filters

@api_router.get("/settings/notifications")
async def get_notification_preferences(user: User = Depends(get_current_user)):
    from models import NotificationPreferences
    if user.notification_preferences:
        return NotificationPreferences(**user.notification_preferences)
    return NotificationPreferences()

@api_router.put("/settings/notifications")
async def update_notification_preferences(prefs: dict, user: User = Depends(get_current_user)):
    from models import NotificationPreferences
    validated = NotificationPreferences(**prefs)
    await db.users.update_one({"id": user.id}, {"$set": {"notification_preferences": validated.model_dump()}})
    return validated

@api_router.get("/categories")
async def get_categories(user: User = Depends(get_current_user)):
    categories = await db.products.distinct("category")
    return categories

# ========== BOARDS ==========
@api_router.post("/boards", response_model=ProductBoard)
async def create_board(name: str, description: Optional[str] = None, user: User = Depends(get_current_user)):
    board = ProductBoard(user_id=user.id, name=name, description=description)
    doc = board.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.boards.insert_one(doc)
    return board

@api_router.get("/boards", response_model=List[ProductBoard])
async def get_boards(user: User = Depends(get_current_user)):
    boards = await db.boards.find({"user_id": user.id}, {"_id": 0}).to_list(100)
    return boards

@api_router.post("/boards/{board_id}/products/{product_id}")
async def add_product_to_board(board_id: str, product_id: str, user: User = Depends(get_current_user)):
    result = await db.boards.update_one(
        {"id": board_id, "user_id": user.id},
        {"$addToSet": {"product_ids": product_id}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Board not found")
    return {"success": True}

@api_router.delete("/boards/{board_id}/products/{product_id}")
async def remove_product_from_board(board_id: str, product_id: str, user: User = Depends(get_current_user)):
    result = await db.boards.update_one(
        {"id": board_id, "user_id": user.id},
        {"$pull": {"product_ids": product_id}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Board not found")
    return {"success": True}

# ========== SCANNER ROUTES ==========
from routes.tiers import check_feature_access, get_tier_limits

@api_router.post("/scan/full")
async def run_full_scan(user: User = Depends(get_current_user)):
    """Run a full AI-powered scan across all sources"""
    if not user.openai_api_key:
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key required. Add your key in Settings to enable scanning."
        )

    from services.ai_scanner import create_scanner

    # Get user's filters
    filters = user.filters if user.filters else {}

    scanner = create_scanner(user.openai_api_key)
    results = await scanner.run_full_scan(filters)

    if not results.get("success"):
        raise HTTPException(status_code=500, detail=results.get("error", "Scan failed"))

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Save scan to history
    scan_record = {
        "user_id": user.id,
        "scan_date": today,
        "scan_type": "full",
        "results_summary": {
            "total_products": results.get("count", 0),
            "source_stats": results.get("source_stats", {}),
        },
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.scan_history.insert_one(scan_record)

    # Store products for dashboard
    import uuid as _uuid
    for product in results.get("products", []):
        product_doc = {
            "id": str(_uuid.uuid4()),
            "user_id": user.id,
            "scan_date": today,
            "is_active": True,
            **product
        }
        await db.daily_products.insert_one(product_doc)

    # Invalidate stale daily report so it regenerates with real data
    await db.daily_reports.delete_many({"user_id": user.id, "date": today})

    # Send Telegram notification if configured
    if user.telegram_bot_token and user.telegram_chat_id:
        from services.telegram_bot import TelegramBot
        bot = TelegramBot()
        bot.bot_token = user.telegram_bot_token
        bot.is_configured = True
        bot.base_url = f"https://api.telegram.org/bot{user.telegram_bot_token}"
        await bot.send_message(
            user.telegram_chat_id,
            f"✅ <b>Scan Complete!</b>\n\nFound {results.get('total_products', 0)} trending products.\n\n📊 Check your dashboard for details."
        )

    return results

@api_router.get("/scan/full/stream")
async def run_full_scan_stream(token: str = None):
    """Run a full scan with Server-Sent Events for real-time progress.
    Uses ?token= query param for auth since EventSource doesn't support headers."""
    if not token:
        raise HTTPException(status_code=401, detail="Token required as query parameter")

    import jwt as _jwt
    try:
        payload = _jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user_doc:
            raise HTTPException(status_code=401, detail="User not found")
        user = User(**user_doc)
    except _jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except _jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if not user.openai_api_key:
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key required."
        )

    import asyncio
    import json as _json
    import uuid as _uuid

    async def event_stream():
        def send(data):
            return f"data: {_json.dumps(data)}\n\n"

        filters = user.filters if user.filters else {}

        # Step 1: Run real scrapers individually with progress updates
        from services.scanners import (
            TikTokScanner, AmazonScanner, AliExpressScanner, GoogleTrendsScanner
        )

        # AI scanner for per-source fallback when scrapers return 0
        from services.ai_scanner import create_scanner
        scanner = create_scanner(user.openai_api_key)

        # Inline per-source scraping with AI fallback when scrapers return 0
        tiktok_products = []
        yield send({"step": "tiktok", "status": "scanning", "message": "Scanning TikTok Creative Center..."})
        try:
            tiktok_products = await TikTokScanner().scan_trending()
            if not tiktok_products:
                yield send({"step": "tiktok", "status": "scanning", "message": "TikTok: scraper returned 0, using AI fallback..."})
                ai_result = await scanner.scan_source("tiktok", filters)
                tiktok_products = ai_result.get("products", [])
                yield send({"step": "tiktok", "status": "done", "count": len(tiktok_products), "message": f"TikTok: AI generated {len(tiktok_products)} products"})
            else:
                yield send({"step": "tiktok", "status": "done", "count": len(tiktok_products), "message": f"TikTok: scraped {len(tiktok_products)} products"})
        except Exception as e:
            try:
                yield send({"step": "tiktok", "status": "scanning", "message": "TikTok: scraper error, using AI fallback..."})
                ai_result = await scanner.scan_source("tiktok", filters)
                tiktok_products = ai_result.get("products", [])
                yield send({"step": "tiktok", "status": "done", "count": len(tiktok_products), "message": f"TikTok: AI generated {len(tiktok_products)} products"})
            except Exception:
                yield send({"step": "tiktok", "status": "error", "message": f"TikTok: {str(e)[:80]}"})

        amazon_products = []
        yield send({"step": "amazon", "status": "scanning", "message": "Scanning Amazon Movers & Shakers..."})
        try:
            amazon_products = await AmazonScanner().scan_movers_shakers()
            if not amazon_products:
                yield send({"step": "amazon", "status": "scanning", "message": "Amazon: scraper returned 0, using AI fallback..."})
                ai_result = await scanner.scan_source("amazon", filters)
                amazon_products = ai_result.get("products", [])
                yield send({"step": "amazon", "status": "done", "count": len(amazon_products), "message": f"Amazon: AI generated {len(amazon_products)} products"})
            else:
                yield send({"step": "amazon", "status": "done", "count": len(amazon_products), "message": f"Amazon: scraped {len(amazon_products)} products"})
        except Exception as e:
            try:
                yield send({"step": "amazon", "status": "scanning", "message": "Amazon: scraper error, using AI fallback..."})
                ai_result = await scanner.scan_source("amazon", filters)
                amazon_products = ai_result.get("products", [])
                yield send({"step": "amazon", "status": "done", "count": len(amazon_products), "message": f"Amazon: AI generated {len(amazon_products)} products"})
            except Exception:
                yield send({"step": "amazon", "status": "error", "message": f"Amazon: {str(e)[:80]}"})

        ali_products = []
        yield send({"step": "aliexpress", "status": "scanning", "message": "Scanning AliExpress trending products..."})
        try:
            ali_products = await AliExpressScanner().scan_trending()
            if not ali_products:
                yield send({"step": "aliexpress", "status": "scanning", "message": "AliExpress: scraper returned 0, using AI fallback..."})
                ai_result = await scanner.scan_source("aliexpress", filters)
                ali_products = ai_result.get("products", [])
                yield send({"step": "aliexpress", "status": "done", "count": len(ali_products), "message": f"AliExpress: AI generated {len(ali_products)} products"})
            else:
                yield send({"step": "aliexpress", "status": "done", "count": len(ali_products), "message": f"AliExpress: scraped {len(ali_products)} products"})
        except Exception as e:
            try:
                yield send({"step": "aliexpress", "status": "scanning", "message": "AliExpress: scraper error, using AI fallback..."})
                ai_result = await scanner.scan_source("aliexpress", filters)
                ali_products = ai_result.get("products", [])
                yield send({"step": "aliexpress", "status": "done", "count": len(ali_products), "message": f"AliExpress: AI generated {len(ali_products)} products"})
            except Exception:
                yield send({"step": "aliexpress", "status": "error", "message": f"AliExpress: {str(e)[:80]}"})

        trends_products = []
        yield send({"step": "google_trends", "status": "scanning", "message": "Scanning Google Trends rising searches..."})
        try:
            trends_products = await GoogleTrendsScanner().scan_rising_terms()
            if not trends_products:
                yield send({"step": "google_trends", "status": "scanning", "message": "Google Trends: scraper returned 0, using AI fallback..."})
                ai_result = await scanner.scan_source("google_trends", filters)
                trends_products = ai_result.get("products", [])
                yield send({"step": "google_trends", "status": "done", "count": len(trends_products), "message": f"Google Trends: AI generated {len(trends_products)} products"})
            else:
                yield send({"step": "google_trends", "status": "done", "count": len(trends_products), "message": f"Google Trends: scraped {len(trends_products)} products"})
        except Exception as e:
            try:
                yield send({"step": "google_trends", "status": "scanning", "message": "Google Trends: scraper error, using AI fallback..."})
                ai_result = await scanner.scan_source("google_trends", filters)
                trends_products = ai_result.get("products", [])
                yield send({"step": "google_trends", "status": "done", "count": len(trends_products), "message": f"Google Trends: AI generated {len(trends_products)} products"})
            except Exception:
                yield send({"step": "google_trends", "status": "error", "message": f"Google Trends: {str(e)[:80]}"})

        all_raw = tiktok_products + amazon_products + ali_products + trends_products
        source_stats = {
            "tiktok": len(tiktok_products),
            "amazon": len(amazon_products),
            "aliexpress": len(ali_products),
            "google_trends": len(trends_products),
        }

        # Step 2: AI enrichment
        # Separate already-enriched (from AI fallback) vs raw scraped products
        ai_fallback_products = [p for p in all_raw if isinstance(p, dict) and p.get("ai_enriched")]
        raw_only = [p for p in all_raw if not (isinstance(p, dict) and p.get("ai_enriched"))]

        yield send({"step": "ai_enrichment", "status": "scanning", "message": f"AI analyzing {len(raw_only)} raw products with GPT-4o..."})

        products = []
        try:
            if raw_only:
                products_summary = _json.dumps(raw_only[:20], default=str)
                system_prompt = """You are a dropshipping product research expert. You will receive real scraped product data.
Your job is to analyze, enrich, and score these products for dropshipping potential.
You MUST respond with a JSON object containing a "products" array."""
                filter_instructions = scanner._build_filter_instructions(filters)
                user_prompt = f"""Real scraped data from multiple sources:

{products_summary}

For each product, provide enriched data:
- name, source, estimated_views, source_cost, recommended_price
- margin_percent, trend_score (1-100), overall_score (1-100), category
- why_trending, saturation_level (low/medium/high), active_fb_ads (number)
- trend_direction (up/down/stable)
{filter_instructions}

Return as JSON: {{"products": [...]}}"""
                result = await scanner._call_openai_json(system_prompt, user_prompt)
                raw_products = result.get("products", [])
                products = [scanner._validate_product(p) for p in raw_products if scanner._validate_product(p)]
                for p in products:
                    p["discovered_at"] = datetime.now(timezone.utc).isoformat()
                    p["ai_enriched"] = True

            # Merge AI fallback products that were already enriched per-source
            products = products + ai_fallback_products

            if not products:
                # Fallback: ask AI to generate from knowledge
                result = await scanner.scan_trending_products(filters)
                products = result.get("products", [])

            yield send({"step": "ai_enrichment", "status": "done", "count": len(products), "message": f"AI enriched {len(products)} products with scores and analysis"})
        except Exception as e:
            yield send({"step": "ai_enrichment", "status": "error", "message": f"AI enrichment: {str(e)[:80]}"})
            products = all_raw[:10]  # Use raw data as fallback

        # Step 3: Save results
        yield send({"step": "saving", "status": "scanning", "message": "Saving results to your dashboard..."})

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        scan_record = {
            "user_id": user.id,
            "scan_date": today,
            "scan_type": "full_stream",
            "results_summary": {
                "total_products": len(products),
                "source_stats": source_stats,
                "raw_products_scraped": len(all_raw),
            },
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.scan_history.insert_one(scan_record)

        for product in products:
            product_doc = {
                "id": str(_uuid.uuid4()),
                "user_id": user.id,
                "scan_date": today,
                "is_active": True,
                **product
            }
            await db.daily_products.insert_one(product_doc)

        # Invalidate stale daily report
        await db.daily_reports.delete_many({"user_id": user.id, "date": today})

        yield send({"step": "saving", "status": "done", "message": f"Saved {len(products)} products"})

        # Step 4: Telegram notification
        if user.telegram_bot_token and user.telegram_chat_id:
            yield send({"step": "telegram", "status": "scanning", "message": "Sending Telegram notification..."})
            try:
                from services.telegram_bot import TelegramBot
                bot = TelegramBot()
                bot.bot_token = user.telegram_bot_token
                bot.is_configured = True
                bot.base_url = f"https://api.telegram.org/bot{user.telegram_bot_token}"
                await bot.send_message(
                    user.telegram_chat_id,
                    f"✅ <b>Scan Complete!</b>\n\nScraped {len(all_raw)} products from {sum(1 for v in source_stats.values() if v > 0)} sources.\nAI selected top {len(products)} opportunities.\n\n📊 Check your dashboard for details."
                )
                yield send({"step": "telegram", "status": "done", "message": "Telegram notification sent"})
            except Exception as e:
                yield send({"step": "telegram", "status": "error", "message": f"Telegram: {str(e)[:80]}"})

        # Final complete event
        yield send({
            "step": "complete",
            "status": "done",
            "message": f"Scan complete! Found {len(products)} products from {len(all_raw)} raw results.",
            "total_products": len(products),
            "source_stats": source_stats,
            "raw_scraped": len(all_raw),
        })

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

@api_router.get("/scan/sources/{source}")
async def scan_single_source(source: str, user: User = Depends(get_current_user)):
    """Scan a single data source with AI"""
    if not user.openai_api_key:
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key required. Add your key in Settings."
        )
    
    valid_sources = ["tiktok", "amazon", "aliexpress", "google_trends"]
    if source not in valid_sources:
        raise HTTPException(status_code=400, detail=f"Invalid source. Must be one of: {valid_sources}")
    
    from services.ai_scanner import create_scanner
    
    filters = user.filters if user.filters else {}
    scanner = create_scanner(user.openai_api_key)
    result = await scanner.scan_source(source, filters)
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Scan failed"))
    
    return result

@api_router.post("/scan/analyze/{product_name}")
async def analyze_product(product_name: str, user: User = Depends(get_current_user)):
    """Deep analysis of a specific product"""
    if not user.openai_api_key:
        raise HTTPException(status_code=400, detail="OpenAI API key required")
    
    from services.ai_scanner import create_scanner
    scanner = create_scanner(user.openai_api_key)
    result = await scanner.analyze_product(product_name)
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Analysis failed"))
    
    return result

@api_router.get("/scan/status")
async def get_scan_status(user: User = Depends(get_current_user)):
    """Get scanning capability status for current user"""
    has_key = bool(user.openai_api_key)
    
    # Get last scan time
    last_scan = await db.scan_history.find_one(
        {"user_id": user.id},
        {"_id": 0, "created_at": 1},
        sort=[("created_at", -1)]
    )
    
    # Calculate next scheduled scan based on tier
    from services.scheduler import TIER_SCAN_FREQUENCY
    frequency = TIER_SCAN_FREQUENCY.get(user.subscription_tier, 24)
    
    return {
        "ai_scanning_available": has_key,
        "openai_key_configured": has_key,
        "telegram_configured": bool(user.telegram_bot_token and user.telegram_chat_id),
        "scan_mode": "ai_powered" if has_key else "disabled",
        "last_scan": last_scan.get("created_at") if last_scan else None,
        "scan_frequency_hours": frequency,
        "next_report": "7:00 AM Eastern daily",
        "message": "AI scanning ready" if has_key else "Add OpenAI API key in Settings to enable scanning"
    }

# ========== AI BROWSER SCAN ENDPOINTS ==========
@api_router.post("/scan/ai-browser/full")
async def run_ai_browser_full_scan(user: User = Depends(get_current_user)):
    """Run full AI browser scan (delegates to regular AI scan)"""
    if not user.openai_api_key:
        raise HTTPException(status_code=400, detail="OpenAI API key required")
    from services.ai_scanner import create_scanner
    scanner = create_scanner(user.openai_api_key)
    filters = user.filters if user.filters else {}
    results = await scanner.run_full_scan(filters)
    if not results.get("success"):
        raise HTTPException(status_code=500, detail=results.get("error", "Scan failed"))
    return results

@api_router.post("/scan/ai-browser/{source}")
async def run_ai_browser_source_scan(
    source: str,
    store_url: Optional[str] = None,
    product_name: Optional[str] = None,
    user: User = Depends(get_current_user)
):
    """Run AI browser scan for a single source"""
    if not user.openai_api_key:
        raise HTTPException(status_code=400, detail="OpenAI API key required")
    valid_sources = ["tiktok", "amazon", "aliexpress", "google_trends", "competitor", "meta-ads"]
    if source not in valid_sources:
        raise HTTPException(status_code=400, detail=f"Invalid source. Must be one of: {valid_sources}")
    from services.ai_scanner import create_scanner
    scanner = create_scanner(user.openai_api_key)
    filters = user.filters if user.filters else {}
    if store_url:
        filters["store_url"] = store_url
    if product_name:
        filters["product_name"] = product_name
    result = await scanner.scan_source(source, filters)
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Scan failed"))
    return result

@api_router.get("/scan/ai-browser/status")
async def get_ai_browser_status(user: User = Depends(get_current_user)):
    """Get AI browser agent status"""
    return {
        "browser_use_available": False,
        "openai_key_configured": bool(user.openai_api_key),
        "is_ready": bool(user.openai_api_key),
        "scan_mode": "ai_powered" if user.openai_api_key else "disabled",
        "message": "AI scanning ready" if user.openai_api_key else "Add OpenAI API key in Settings"
    }

# ========== COMPETITOR SPY ==========
from services.competitor_spy import (
    CompetitorStore, CompetitorAlert, CompetitorProduct,
    scrape_shopify_store, detect_store_changes
)

@api_router.post("/competitors")
async def add_competitor(store_url: str, user: User = Depends(get_current_user)):
    check_feature_access(user.subscription_tier, "competitor_spy")
    
    # Check competitor limit
    limits = get_tier_limits(user.subscription_tier)
    if limits["competitors"] != -1:
        current_count = await db.competitors.count_documents({"user_id": user.id, "is_active": True})
        if current_count >= limits["competitors"]:
            raise HTTPException(
                status_code=403, 
                detail=f"Competitor limit reached ({limits['competitors']}). Upgrade for more."
            )
    
    existing = await db.competitors.find_one({"user_id": user.id, "store_url": store_url})
    if existing:
        raise HTTPException(status_code=400, detail="Already monitoring this store")
    
    store_data = await scrape_shopify_store(store_url)
    
    competitor = CompetitorStore(
        user_id=user.id,
        store_url=store_url,
        store_name=store_data["store_name"],
        products_snapshot=[p["name"] for p in store_data["products"]],
        last_scanned=datetime.now(timezone.utc)
    )
    
    doc = competitor.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['last_scanned'] = doc['last_scanned'].isoformat()
    await db.competitors.insert_one(doc)
    
    for product in store_data["products"]:
        prod = CompetitorProduct(
            competitor_id=competitor.id,
            name=product["name"],
            price=product["price"]
        )
        prod_doc = prod.model_dump()
        prod_doc['first_seen'] = prod_doc['first_seen'].isoformat()
        prod_doc['last_seen'] = prod_doc['last_seen'].isoformat()
        await db.competitor_products.insert_one(prod_doc)
    
    return {"competitor": competitor.model_dump(), "store_data": store_data}

@api_router.get("/competitors")
async def get_competitors(user: User = Depends(get_current_user)):
    competitors = await db.competitors.find({"user_id": user.id, "is_active": True}, {"_id": 0}).to_list(50)
    return competitors

@api_router.get("/competitors/{competitor_id}")
async def get_competitor(competitor_id: str, user: User = Depends(get_current_user)):
    competitor = await db.competitors.find_one({"id": competitor_id, "user_id": user.id}, {"_id": 0})
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    products = await db.competitor_products.find({"competitor_id": competitor_id}, {"_id": 0}).to_list(100)
    return {"competitor": competitor, "products": products, "total_products": len(products)}

@api_router.post("/competitors/{competitor_id}/scan")
async def scan_competitor(competitor_id: str, user: User = Depends(get_current_user)):
    competitor = await db.competitors.find_one({"id": competitor_id, "user_id": user.id}, {"_id": 0})
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    store_data = await scrape_shopify_store(competitor["store_url"])
    old_products = competitor.get("products_snapshot", [])
    changes = detect_store_changes(old_products, store_data["products"])
    
    await db.competitors.update_one(
        {"id": competitor_id},
        {
            "$set": {
                "products_snapshot": [p["name"] for p in store_data["products"]],
                "last_scanned": datetime.now(timezone.utc).isoformat(),
                "new_products_count": changes["added_count"]
            }
        }
    )
    
    if changes["added_count"] > 0:
        alert = CompetitorAlert(
            user_id=user.id,
            competitor_id=competitor_id,
            competitor_name=competitor["store_name"],
            alert_type="new_product",
            title=f"New products at {competitor['store_name']}",
            message=f"{changes['added_count']} new product(s) detected",
            product_data={"new_products": changes["added_products"]}
        )
        alert_doc = alert.model_dump()
        alert_doc['created_at'] = alert_doc['created_at'].isoformat()
        await db.competitor_alerts.insert_one(alert_doc)
    
    return {"changes": changes, "store_data": store_data, "scanned_at": datetime.now(timezone.utc).isoformat()}

@api_router.delete("/competitors/{competitor_id}")
async def remove_competitor(competitor_id: str, user: User = Depends(get_current_user)):
    result = await db.competitors.update_one(
        {"id": competitor_id, "user_id": user.id},
        {"$set": {"is_active": False}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Competitor not found")
    return {"success": True}

@api_router.get("/competitors/alerts/all")
async def get_all_alerts(user: User = Depends(get_current_user)):
    alerts = await db.competitor_alerts.find({"user_id": user.id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return alerts

@api_router.put("/competitors/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: str, user: User = Depends(get_current_user)):
    result = await db.competitor_alerts.update_one(
        {"id": alert_id, "user_id": user.id},
        {"$set": {"is_read": True}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"success": True}

# ========== SATURATION RADAR ==========
@api_router.get("/saturation/overview")
async def get_saturation_overview(user: User = Depends(get_current_user)):
    check_feature_access(user.subscription_tier, "saturation_radar")

    # Get user's scanned products first, then fall back to seed products
    products = await db.daily_products.find(
        {"user_id": user.id, "is_active": True}, {"_id": 0}
    ).to_list(100)
    if not products:
        products = await db.daily_products.find(
            {"is_active": True}, {"_id": 0}
        ).to_list(100)
    if not products:
        products = await db.products.find({}, {"_id": 0}).to_list(100)

    saturation_data = {"low": [], "medium": [], "high": []}

    for product in products:
        level = product.get("saturation_level", "medium")
        if level not in saturation_data:
            level = "medium"
        saturation_data[level].append({
            "id": product.get("id", ""),
            "name": product.get("name", "Unknown"),
            "fb_ads": product.get("active_fb_ads", 0),
            "shopify_stores": product.get("shopify_stores", 0),
            "trend_direction": product.get("trend_direction", "stable")
        })

    return {
        "overview": saturation_data,
        "stats": {
            "low_competition": len(saturation_data["low"]),
            "medium_competition": len(saturation_data["medium"]),
            "high_competition": len(saturation_data["high"])
        }
    }

@api_router.get("/saturation/niches")
async def get_niche_saturation(user: User = Depends(get_current_user)):
    check_feature_access(user.subscription_tier, "saturation_radar")

    # Get user's scanned products first, then fall back to seed products
    products = await db.daily_products.find(
        {"user_id": user.id, "is_active": True}, {"_id": 0}
    ).to_list(100)
    if not products:
        products = await db.daily_products.find(
            {"is_active": True}, {"_id": 0}
        ).to_list(100)
    if not products:
        products = await db.products.find({}, {"_id": 0}).to_list(100)

    niche_data = {}
    for product in products:
        category = product.get("category", "Other")
        if category not in niche_data:
            niche_data[category] = {"total_products": 0, "avg_fb_ads": 0, "avg_stores": 0, "saturation_score": 0}

        niche_data[category]["total_products"] += 1
        niche_data[category]["avg_fb_ads"] += product.get("active_fb_ads", 0)
        niche_data[category]["avg_stores"] += product.get("shopify_stores", 0)

    for category in niche_data:
        count = niche_data[category]["total_products"]
        if count > 0:
            niche_data[category]["avg_fb_ads"] = round(niche_data[category]["avg_fb_ads"] / count)
            niche_data[category]["avg_stores"] = round(niche_data[category]["avg_stores"] / count)
            niche_data[category]["saturation_score"] = min(100, (niche_data[category]["avg_fb_ads"] + niche_data[category]["avg_stores"]) // 3)

    return niche_data

# ========== TELEGRAM ==========
@api_router.get("/telegram/status")
async def get_telegram_status(user: User = Depends(get_current_user)):
    return {
        "has_bot_token": bool(user.telegram_bot_token),
        "has_chat_id": bool(user.telegram_chat_id),
        "is_ready": bool(user.telegram_bot_token and user.telegram_chat_id)
    }

@api_router.post("/telegram/test")
async def test_telegram(user: User = Depends(get_current_user)):
    check_feature_access(user.subscription_tier, "telegram_alerts")
    if not user.telegram_bot_token:
        raise HTTPException(status_code=400, detail="Add your Telegram Bot Token first")
    if not user.telegram_chat_id:
        raise HTTPException(status_code=400, detail="Add your Telegram Chat ID first")
    
    from services.telegram_bot import TelegramBot
    user_bot = TelegramBot()
    user_bot.bot_token = user.telegram_bot_token
    user_bot.is_configured = True
    user_bot.base_url = f"https://api.telegram.org/bot{user.telegram_bot_token}"
    
    result = await user_bot.send_message(
        user.telegram_chat_id,
        "🎉 <b>DropSniper AI Connected!</b>\n\nYour bot is working! You'll receive daily reports and alerts here."
    )
    
    # Return detailed error if failed
    if not result.get("success"):
        detail = result.get("detail", result.get("error", "Failed to send message"))
        raise HTTPException(status_code=400, detail=detail)
    
    return {"success": True, "message": "Test message sent successfully!"}

@api_router.post("/telegram/send-report")
async def send_telegram_report(user: User = Depends(get_current_user)):
    check_feature_access(user.subscription_tier, "telegram_alerts")
    if not user.telegram_bot_token or not user.telegram_chat_id:
        raise HTTPException(status_code=400, detail="Configure your Telegram bot token and chat ID first")
    
    from services.telegram_bot import TelegramBot
    user_bot = TelegramBot()
    user_bot.bot_token = user.telegram_bot_token
    user_bot.is_configured = True
    user_bot.base_url = f"https://api.telegram.org/bot{user.telegram_bot_token}"
    
    # Get user's scanned products (today or most recent)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    products = await db.daily_products.find(
        {"user_id": user.id, "scan_date": today},
        {"_id": 0}
    ).sort("trend_score", -1).limit(5).to_list(5)
    
    # Fallback to any recent products
    if not products:
        products = await db.daily_products.find(
            {"user_id": user.id},
            {"_id": 0}
        ).sort("discovered_at", -1).limit(5).to_list(5)
    
    # Fallback to seed products if no daily products exist
    if not products:
        products = await db.products.find({}, {"_id": 0}).sort("overall_score", -1).limit(5).to_list(5)

    if not products:
        raise HTTPException(status_code=400, detail="No products found. Run a scan first!")

    # Get real scan stats
    today_product_count = await db.daily_products.count_documents({"user_id": user.id, "scan_date": today})

    report_data = {
        "products_scanned": today_product_count or len(products),
        "passed_filters": len(products),
        "fully_validated": len(products),
        "ready_to_launch": len(products),
        "top_products": [
            {
                "name": p.get("name", "Unknown"),
                "score": p.get("trend_score", p.get("overall_score", 0)),
                "source_cost": p.get("source_cost", 0),
                "sell_price": p.get("recommended_price", 0),
                "margin": p.get("margin_percent", 0),
                "fb_ads": p.get("estimated_views", 0) // 100000,
                "trend_direction": "up" if p.get("trend_score", 0) > 70 else "stable",
                "trend_percent": p.get("trend_score", 0)
            }
            for p in products
        ],
        "alerts": []
    }
    
    result = await user_bot.send_daily_report(user.telegram_chat_id, report_data)
    return result

@api_router.post("/telegram/send-launch-kit/{kit_id}")
async def send_launch_kit_telegram(kit_id: str, user: User = Depends(get_current_user)):
    """Send a launch kit summary via Telegram"""
    check_feature_access(user.subscription_tier, "telegram_alerts")
    if not user.telegram_bot_token or not user.telegram_chat_id:
        raise HTTPException(status_code=400, detail="Configure your Telegram bot token and chat ID first")

    kit = await db.launch_kits.find_one({"id": kit_id, "user_id": user.id}, {"_id": 0})
    if not kit:
        raise HTTPException(status_code=404, detail="Launch kit not found")

    from services.telegram_bot import TelegramBot
    user_bot = TelegramBot()
    user_bot.bot_token = user.telegram_bot_token
    user_bot.is_configured = True
    user_bot.base_url = f"https://api.telegram.org/bot{user.telegram_bot_token}"

    result = await user_bot.send_launch_kit_summary(user.telegram_chat_id, kit)
    if not result.get("success"):
        detail = result.get("detail", result.get("error", "Failed to send message"))
        raise HTTPException(status_code=400, detail=detail)

    return {"success": True, "message": "Launch kit sent to Telegram!"}

# ========== INTEGRATIONS STATUS ==========
@api_router.get("/integrations/status")
async def get_integrations_status(user: User = Depends(get_current_user)):
    return {
        "openai_configured": bool(user.openai_api_key),
        "telegram_configured": bool(user.telegram_bot_token and user.telegram_chat_id),
        "telegram_bot_token_set": bool(user.telegram_bot_token),
        "telegram_chat_id_set": bool(user.telegram_chat_id),
    }

# ========== SEED DATA ==========
@api_router.post("/seed")
async def seed_data():
    count = await db.products.count_documents({})
    if count > 0:
        return {"message": "Data already seeded", "count": count}
    
    sample_products = [
        Product(name="Portable Neck Fan", category="Electronics", image_url="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400", description="Rechargeable bladeless neck fan with 3 speed settings.", source_cost=6.20, recommended_price=34.99, margin_percent=72, suppliers=[Supplier(name="TechGadgets Store", platform="aliexpress", unit_cost=6.20, shipping_cost=2.30, shipping_days="12-18", rating=4.8, total_orders=12400)], overall_score=94, trend_score=95, competition_score=90, profit_score=92, trend_direction="up", trend_percent=340, search_volume=125000, active_fb_ads=18, shopify_stores=45, saturation_level="low", source_platforms=["tiktok", "amazon"]),
        Product(name="LED Book Lamp", category="Home & Garden", image_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400", description="Wooden folding book lamp with warm LED light.", source_cost=11.40, recommended_price=44.99, margin_percent=68, suppliers=[Supplier(name="HomeDecor Factory", platform="aliexpress", unit_cost=11.40, shipping_cost=3.20, shipping_days="14-20", rating=4.6, total_orders=7800)], overall_score=89, trend_score=85, competition_score=82, profit_score=88, trend_direction="up", trend_percent=180, search_volume=89000, active_fb_ads=34, shopify_stores=62, saturation_level="medium", source_platforms=["pinterest", "amazon"]),
        Product(name="Cloud Slides", category="Fashion", image_url="https://images.unsplash.com/photo-1603808033192-082d6919d3e1?w=400", description="Ultra-soft pillow slides with thick sole.", source_cost=8.90, recommended_price=38.99, margin_percent=65, suppliers=[Supplier(name="FashionWear Co", platform="aliexpress", unit_cost=8.90, shipping_cost=2.80, shipping_days="10-15", rating=4.7, total_orders=25000)], overall_score=86, trend_score=92, competition_score=70, profit_score=85, trend_direction="up", trend_percent=95, search_volume=210000, active_fb_ads=42, shopify_stores=120, saturation_level="medium", source_platforms=["tiktok", "google_trends"]),
        Product(name="Mini Projector", category="Electronics", image_url="https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=400", description="Portable HD projector with WiFi.", source_cost=45.00, recommended_price=129.99, margin_percent=58, suppliers=[Supplier(name="ElectroHub", platform="aliexpress", unit_cost=45.00, shipping_cost=8.00, shipping_days="15-20", rating=4.5, total_orders=9200)], overall_score=82, trend_score=78, competition_score=75, profit_score=80, trend_direction="stable", trend_percent=15, search_volume=340000, active_fb_ads=85, shopify_stores=200, saturation_level="high", source_platforms=["amazon", "aliexpress"]),
        Product(name="Posture Corrector", category="Health & Wellness", image_url="https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400", description="Adjustable back brace for improved posture.", source_cost=5.50, recommended_price=29.99, margin_percent=75, suppliers=[Supplier(name="HealthFirst", platform="aliexpress", unit_cost=5.50, shipping_cost=1.80, shipping_days="12-16", rating=4.6, total_orders=18000)], overall_score=79, trend_score=65, competition_score=72, profit_score=88, trend_direction="down", trend_percent=-12, search_volume=156000, active_fb_ads=95, shopify_stores=180, saturation_level="high", source_platforms=["amazon", "google_trends"]),
        Product(name="Magnetic Phone Mount", category="Electronics", image_url="https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=400", description="360° rotating magnetic car mount.", source_cost=4.20, recommended_price=24.99, margin_percent=78, suppliers=[Supplier(name="AutoAccessories", platform="aliexpress", unit_cost=4.20, shipping_cost=1.50, shipping_days="10-14", rating=4.7, total_orders=32000)], overall_score=85, trend_score=80, competition_score=85, profit_score=90, trend_direction="up", trend_percent=45, search_volume=98000, active_fb_ads=28, shopify_stores=55, saturation_level="low", source_platforms=["amazon", "aliexpress"]),
        Product(name="Smart Water Bottle", category="Health & Wellness", image_url="https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400", description="LED temperature display water bottle.", source_cost=7.80, recommended_price=32.99, margin_percent=70, suppliers=[Supplier(name="SmartLife Store", platform="aliexpress", unit_cost=7.80, shipping_cost=2.40, shipping_days="12-18", rating=4.5, total_orders=8900)], overall_score=88, trend_score=88, competition_score=85, profit_score=86, trend_direction="up", trend_percent=120, search_volume=67000, active_fb_ads=22, shopify_stores=38, saturation_level="low", source_platforms=["tiktok", "amazon"]),
        Product(name="Sunset Lamp Projector", category="Home & Garden", image_url="https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=400", description="USB sunset projection lamp for ambient lighting.", source_cost=6.50, recommended_price=28.99, margin_percent=72, suppliers=[Supplier(name="LightingWorld", platform="aliexpress", unit_cost=6.50, shipping_cost=2.00, shipping_days="10-15", rating=4.8, total_orders=45000)], overall_score=91, trend_score=94, competition_score=88, profit_score=90, trend_direction="up", trend_percent=280, search_volume=185000, active_fb_ads=35, shopify_stores=78, saturation_level="medium", source_platforms=["tiktok", "pinterest"])
    ]
    
    for product in sample_products:
        doc = product.model_dump()
        doc['discovered_at'] = doc['discovered_at'].isoformat()
        doc['last_updated'] = doc['last_updated'].isoformat()
        await db.products.insert_one(doc)
    
    return {"message": "Seeded successfully", "count": len(sample_products)}

# ========== HEALTH CHECK ==========
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Include router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
