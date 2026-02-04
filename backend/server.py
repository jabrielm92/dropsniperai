"""DropSniper AI - Main FastAPI Application"""
from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
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

# JWT Config
JWT_SECRET = os.environ.get('JWT_SECRET', secrets.token_hex(32))

# Initialize route dependencies
from routes.deps import init_db, get_current_user, get_db
init_db(db, JWT_SECRET)

# Create app
app = FastAPI(title="DropSniper AI API", version="2.0.0")

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Start background scheduler on startup
@app.on_event("startup")
async def startup_event():
    from services.scheduler import start_scheduler
    try:
        start_scheduler(db)
        logger.info("Background scheduler started")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")

# CORS - Read from environment or allow specific origins
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
if CORS_ORIGINS == '*':
    origins = ["*"]
else:
    origins = [origin.strip() for origin in CORS_ORIGINS.split(',')]

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

# ========== AUTH ME ENDPOINT ==========
@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return UserResponse(
        id=user.id, 
        email=user.email, 
        name=user.name, 
        subscription_tier=user.subscription_tier, 
        is_admin=user.is_admin,
        telegram_chat_id=user.telegram_chat_id,
        has_openai_key=bool(user.openai_api_key),
        has_telegram_token=bool(user.telegram_bot_token)
    )

# ========== LAUNCH KIT ROUTES ==========
@api_router.post("/launch-kit/{product_id}", response_model=LaunchKit)
async def generate_launch_kit(product_id: str, user: User = Depends(get_current_user)):
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
        products = await db.products.find({}, {"_id": 0}).sort("overall_score", -1).limit(5).to_list(5)
        top_ids = [p['id'] for p in products]
        
        report = DailyReport(
            user_id=user.id,
            date=today,
            products_scanned=2847,
            passed_filters=23,
            fully_validated=7,
            ready_to_launch=len(top_ids),
            top_products=top_ids,
            alerts=[
                {"type": "competition", "product": "Galaxy Projector", "message": "Competition ↑ 15 new ads detected"},
                {"type": "trend", "product": "Posture Corrector", "message": "Search volume declining 12%"}
            ]
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
    
    # Save scan to history
    scan_record = {
        "user_id": user.id,
        "scan_type": "full",
        "results": results,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.scan_history.insert_one(scan_record)
    
    # Store products for dashboard
    for product in results.get("products", []):
        product_doc = {
            "user_id": user.id,
            "scan_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "is_active": True,
            **product
        }
        await db.daily_products.insert_one(product_doc)
    
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
    from services.ai_browser_agent import create_agent_for_user, BROWSER_USE_AVAILABLE
    
    # AI-powered scan if user has key
    if user.openai_api_key and BROWSER_USE_AVAILABLE:
        agent = create_agent_for_user(user.openai_api_key)
        if source == "tiktok":
            result = await agent.scan_tiktok_trending()
        elif source == "amazon":
            result = await agent.scan_amazon_movers()
        elif source == "aliexpress":
            result = await agent.scan_aliexpress_trending()
        elif source == "google_trends":
            result = await agent.scan_google_trends()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown source: {source}")
        return {"source": source, "result": result, "scan_mode": "ai_powered"}
    
    # Fallback to mock data
    if source == "tiktok":
        products = await scout_engine.tiktok.scan_trending()
    elif source == "amazon":
        products = await scout_engine.amazon.scan_movers_shakers()
    elif source == "aliexpress":
        products = await scout_engine.aliexpress.scan_trending()
    elif source == "google_trends":
        products = await scout_engine.google_trends.scan_rising_terms()
    else:
        raise HTTPException(status_code=400, detail=f"Unknown source: {source}")
    
    return {"source": source, "products": products, "count": len(products), "scan_mode": "sample_data"}

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
    
    return {
        "ai_scanning_available": has_key,
        "openai_key_configured": has_key,
        "scan_mode": "ai_powered" if has_key else "disabled",
        "message": "AI scanning ready" if has_key else "Add OpenAI API key in Settings to enable scanning"
    }

# ========== COMPETITOR SPY ==========
from services.competitor_spy import (
    CompetitorStore, CompetitorAlert, CompetitorProduct,
    generate_mock_competitor_data, detect_store_changes
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
    
    store_data = generate_mock_competitor_data(store_url)
    
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
    
    store_data = generate_mock_competitor_data(competitor["store_url"])
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
    products = await db.products.find({}, {"_id": 0}).to_list(100)
    
    saturation_data = {"low": [], "medium": [], "high": []}
    
    for product in products:
        level = product.get("saturation_level", "medium")
        saturation_data[level].append({
            "id": product["id"],
            "name": product["name"],
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
    if not user.telegram_bot_token or not user.telegram_chat_id:
        raise HTTPException(status_code=400, detail="Configure your Telegram bot token and chat ID first")
    
    from services.telegram_bot import TelegramBot
    user_bot = TelegramBot()
    user_bot.bot_token = user.telegram_bot_token
    user_bot.is_configured = True
    user_bot.base_url = f"https://api.telegram.org/bot{user.telegram_bot_token}"
    
    products = await db.products.find({}, {"_id": 0}).sort("overall_score", -1).limit(5).to_list(5)
    
    report_data = {
        "products_scanned": 2847,
        "passed_filters": 23,
        "fully_validated": 7,
        "ready_to_launch": len(products),
        "top_products": [
            {
                "name": p["name"],
                "score": p["overall_score"],
                "source_cost": p["source_cost"],
                "sell_price": p["recommended_price"],
                "margin": p["margin_percent"],
                "fb_ads": p["active_fb_ads"],
                "trend_direction": p["trend_direction"],
                "trend_percent": p["trend_percent"]
            }
            for p in products
        ],
        "alerts": [
            {"product": "Galaxy Projector", "message": "Competition ↑ 15 new ads"},
            {"product": "Posture Corrector", "message": "Search volume declining 12%"}
        ]
    }
    
    result = await user_bot.send_daily_report(user.telegram_chat_id, report_data)
    return result

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

# ========== DAILY PRODUCTS (ARCHIVED) ==========
@api_router.get("/products/today")
async def get_today_products(user: User = Depends(get_current_user)):
    """Get today's discovered products"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # First try daily_products collection
    products = await db.daily_products.find(
        {"scan_date": today, "is_active": True},
        {"_id": 0}
    ).sort("overall_score", -1).limit(5).to_list(5)
    
    # Fallback to seed products if no daily products yet
    if not products:
        products = await db.products.find({}, {"_id": 0}).sort("overall_score", -1).limit(5).to_list(5)
    
    return {"date": today, "products": products, "count": len(products)}

@api_router.get("/products/history")
async def get_product_history(
    days: int = 30,
    user: User = Depends(get_current_user)
):
    """Get archived products from past days"""
    # Get distinct scan dates
    dates = await db.daily_products.distinct("scan_date")
    dates = sorted(dates, reverse=True)[:days]
    
    history = []
    for date in dates:
        products = await db.daily_products.find(
            {"scan_date": date},
            {"_id": 0}
        ).sort("overall_score", -1).to_list(10)
        
        if products:
            history.append({
                "date": date,
                "products": products,
                "count": len(products)
            })
    
    # Include seed products as "all time" if no history
    if not history:
        seed_products = await db.products.find({}, {"_id": 0}).sort("overall_score", -1).to_list(20)
        history.append({
            "date": "seed_data",
            "products": seed_products,
            "count": len(seed_products)
        })
    
    return {"history": history, "total_days": len(history)}

@api_router.get("/products/archive/{date}")
async def get_archived_products(date: str, user: User = Depends(get_current_user)):
    """Get products from a specific date"""
    products = await db.daily_products.find(
        {"scan_date": date},
        {"_id": 0}
    ).sort("overall_score", -1).to_list(20)
    
    return {"date": date, "products": products, "count": len(products)}

# ========== HEALTH CHECK ==========
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Include router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
