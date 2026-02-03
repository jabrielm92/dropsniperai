"""
Telegram Bot Service - Sends daily reports and alerts to Telegram
"""
import os
import httpx
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()


class TelegramBot:
    """
    Telegram bot for sending product alerts and daily reports.
    Replicates the ClawdBot Telegram integration from the original X post.
    """
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.is_configured = bool(self.bot_token)
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None
    
    async def send_message(self, chat_id: str, text: str, parse_mode: str = "HTML") -> Dict[str, Any]:
        """Send a message to a Telegram chat"""
        if not self.is_configured:
            return {"error": "Telegram bot not configured", "success": False}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": text,
                        "parse_mode": parse_mode
                    }
                )
                return {"success": response.status_code == 200, "response": response.json()}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def send_daily_report(self, chat_id: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send the daily intelligence report to Telegram"""
        if not self.is_configured:
            return {"error": "Telegram bot not configured", "success": False}
        
        # Format the daily report message
        message = f"""
🌅 <b>GOOD MORNING! YOUR DAILY PRODUCT INTELLIGENCE</b>
📅 {datetime.now(timezone.utc).strftime('%B %d, %Y')}

📊 <b>OVERNIGHT SCAN RESULTS:</b>
├── Products Scanned: <b>{report_data.get('products_scanned', 0):,}</b>
├── Passed Filters: <b>{report_data.get('passed_filters', 0)}</b>
├── Fully Validated: <b>{report_data.get('fully_validated', 0)}</b>
└── Ready to Launch: <b>{report_data.get('ready_to_launch', 0)}</b> ⭐

🔥 <b>TOP OPPORTUNITIES:</b>
"""
        # Add top products
        top_products = report_data.get('top_products', [])
        for i, product in enumerate(top_products[:5], 1):
            trend_emoji = "📈" if product.get('trend_direction') == 'up' else "📉" if product.get('trend_direction') == 'down' else "➡️"
            message += f"""
<b>#{i} {product.get('name', 'Unknown')}</b> (Score: {product.get('score', 0)}/100)
├── Source: ${product.get('source_cost', 0):.2f} | Sell: ${product.get('sell_price', 0):.2f}
├── Margin: {product.get('margin', 0)}% | FB Ads: {product.get('fb_ads', 0)}
└── Trend: {trend_emoji} {product.get('trend_percent', 0):+}%
"""
        
        # Add alerts if any
        alerts = report_data.get('alerts', [])
        if alerts:
            message += "\n⚠️ <b>ALERTS:</b>\n"
            for alert in alerts[:3]:
                message += f"• {alert.get('product', 'Unknown')}: {alert.get('message', '')}\n"
        
        message += "\n💬 Reply with product number to get launch kit!"
        
        return await self.send_message(chat_id, message)
    
    async def send_product_alert(self, chat_id: str, product: Dict[str, Any], alert_type: str) -> Dict[str, Any]:
        """Send a product alert (new opportunity, competition change, etc.)"""
        if not self.is_configured:
            return {"error": "Telegram bot not configured", "success": False}
        
        emoji_map = {
            "new_opportunity": "🚀",
            "competition_increase": "⚠️",
            "trend_spike": "📈",
            "price_drop": "💰",
            "saturation_warning": "🛑"
        }
        
        emoji = emoji_map.get(alert_type, "📢")
        
        message = f"""
{emoji} <b>PRODUCT ALERT: {alert_type.replace('_', ' ').upper()}</b>

<b>{product.get('name', 'Unknown Product')}</b>
├── Score: {product.get('score', 0)}/100
├── Source Cost: ${product.get('source_cost', 0):.2f}
├── Sell Price: ${product.get('sell_price', 0):.2f}
├── Margin: {product.get('margin', 0)}%
└── Competition: {product.get('fb_ads', 0)} FB Ads

{product.get('alert_message', '')}

Reply "LAUNCH {product.get('id', '')}" to generate launch kit
"""
        
        return await self.send_message(chat_id, message)
    
    async def send_competitor_alert(self, chat_id: str, competitor_name: str, new_products: List[Dict]) -> Dict[str, Any]:
        """Send alert when a competitor adds new products"""
        if not self.is_configured:
            return {"error": "Telegram bot not configured", "success": False}
        
        message = f"""
🕵️ <b>COMPETITOR ALERT: {competitor_name}</b>

New products detected:
"""
        for product in new_products[:5]:
            message += f"• {product.get('name', 'Unknown')} - ${product.get('price', 0):.2f}\n"
        
        if len(new_products) > 5:
            message += f"\n...and {len(new_products) - 5} more products"
        
        message += "\n\nView full details in your dashboard."
        
        return await self.send_message(chat_id, message)
    
    async def send_launch_kit_summary(self, chat_id: str, kit: Dict[str, Any]) -> Dict[str, Any]:
        """Send a launch kit summary"""
        if not self.is_configured:
            return {"error": "Telegram bot not configured", "success": False}
        
        message = f"""
🚀 <b>LAUNCH KIT READY: {kit.get('product_name', 'Product')}</b>

📝 <b>Ad Copy Variations:</b> {len(kit.get('ad_copies', []))}
🎬 <b>Video Scripts:</b> {len(kit.get('video_scripts', []))}
🎯 <b>Target Audiences:</b> {len(kit.get('target_audiences', []))}

💰 <b>Pricing Tiers:</b>
"""
        for tier, price in kit.get('pricing_tiers', {}).items():
            message += f"• {tier.replace('_', ' ').title()}: ${price:.2f}\n"
        
        message += f"""
✅ <b>Launch Checklist:</b> {len(kit.get('launch_checklist', []))} items

View full launch kit in your dashboard!
"""
        
        return await self.send_message(chat_id, message)
    
    async def get_updates(self, offset: Optional[int] = None) -> Dict[str, Any]:
        """Get updates (messages) sent to the bot"""
        if not self.is_configured:
            return {"error": "Telegram bot not configured", "success": False}
        
        try:
            params = {}
            if offset:
                params["offset"] = offset
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/getUpdates",
                    params=params
                )
                return {"success": response.status_code == 200, "updates": response.json()}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def get_status(self) -> Dict[str, Any]:
        """Get the configuration status of the Telegram bot"""
        return {
            "configured": self.is_configured,
            "message": "Telegram bot ready" if self.is_configured else "Add TELEGRAM_BOT_TOKEN to enable"
        }


# Singleton instance
telegram_bot = TelegramBot()
