from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
import jwt
import hashlib
import secrets
from typing import List, Optional

from models import (
    User, UserCreate, UserLogin, UserResponse, TokenResponse,
    Product, ProductBrief, LaunchKit, AdCopy, VideoScript,
    DailyReport, ProductBoard, FilterSettings, Supplier
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Config
JWT_SECRET = os.environ.get('JWT_SECRET', secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

app = FastAPI(title="ProductScout AI API")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Helper functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user_doc:
            raise HTTPException(status_code=401, detail="User not found")
        return User(**user_doc)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Auth Routes
@api_router.post("/auth/register", response_model=TokenResponse)
async def register(data: UserCreate):
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=data.email,
        name=data.name,
        password_hash=hash_password(data.password)
    )
    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.users.insert_one(doc)
    
    token = create_token(user.id)
    return TokenResponse(
        access_token=token,
        user=UserResponse(id=user.id, email=user.email, name=user.name, subscription_tier=user.subscription_tier)
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(data: UserLogin):
    user_doc = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user_doc or user_doc['password_hash'] != hash_password(data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user_doc['id'])
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user_doc['id'],
            email=user_doc['email'],
            name=user_doc['name'],
            subscription_tier=user_doc.get('subscription_tier', 'free')
        )
    )

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return UserResponse(id=user.id, email=user.email, name=user.name, subscription_tier=user.subscription_tier, telegram_chat_id=user.telegram_chat_id)

# Products Routes
@api_router.get("/products", response_model=List[Product])
async def get_products(
    category: Optional[str] = None,
    min_score: Optional[int] = None,
    limit: int = 50,
    user: User = Depends(get_current_user)
):
    query = {}
    if category:
        query["category"] = category
    if min_score:
        query["overall_score"] = {"$gte": min_score}
    
    products = await db.products.find(query, {"_id": 0}).sort("overall_score", -1).limit(limit).to_list(limit)
    return products

@api_router.get("/products/top", response_model=List[Product])
async def get_top_products(limit: int = 5, user: User = Depends(get_current_user)):
    products = await db.products.find({}, {"_id": 0}).sort("overall_score", -1).limit(limit).to_list(limit)
    return products

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str, user: User = Depends(get_current_user)):
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@api_router.get("/products/{product_id}/brief", response_model=ProductBrief)
async def get_product_brief(product_id: str, user: User = Depends(get_current_user)):
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_obj = Product(**product)
    best_supplier = product_obj.suppliers[0] if product_obj.suppliers else Supplier(
        name="Generic Supplier", platform="aliexpress", unit_cost=product_obj.source_cost,
        shipping_cost=2.50, shipping_days="10-15", rating=4.5, total_orders=5000
    )
    
    total_cost = best_supplier.unit_cost + best_supplier.shipping_cost
    gross_margin = product_obj.recommended_price - total_cost
    estimated_cpa = 8.0
    net_profit = gross_margin - estimated_cpa
    
    return ProductBrief(
        product_id=product_obj.id,
        product_name=product_obj.name,
        best_supplier=best_supplier,
        alternative_suppliers=product_obj.suppliers[1:] if len(product_obj.suppliers) > 1 else [],
        unit_cost=best_supplier.unit_cost,
        shipping_cost=best_supplier.shipping_cost,
        total_cost=total_cost,
        recommended_price=product_obj.recommended_price,
        gross_margin=gross_margin,
        estimated_ad_cpa=estimated_cpa,
        net_profit_per_unit=net_profit,
        break_even_roas=round(product_obj.recommended_price / (total_cost + estimated_cpa), 2),
        trademark_clear=not product_obj.trademark_risk,
        supplier_verified=True,
        shipping_reasonable=True,
        competition_acceptable=product_obj.active_fb_ads < 50,
        trend_positive=product_obj.trend_direction == "up"
    )

# Launch Kit Routes
@api_router.post("/launch-kit/{product_id}", response_model=LaunchKit)
async def generate_launch_kit(product_id: str, user: User = Depends(get_current_user)):
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_obj = Product(**product)
    
    # Generate launch kit content (placeholder - will be AI-enhanced later)
    launch_kit = LaunchKit(
        product_id=product_id,
        user_id=user.id,
        product_name=product_obj.name,
        product_description=product_obj.description or f"High-quality {product_obj.name} - trending now!",
        ad_copies=[
            AdCopy(style="short", headline=f"🔥 {product_obj.name} - Limited Stock!", body=f"Get yours before it's gone. {int(product_obj.margin_percent)}% OFF today only!", cta="Shop Now"),
            AdCopy(style="long", headline=f"Why Everyone's Talking About {product_obj.name}", body=f"Join thousands of happy customers. Premium quality at an unbeatable price. Free shipping on orders over $50. 30-day money back guarantee.", cta="Get Yours Today"),
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
        upsell_suggestions=[
            "Extended warranty package",
            "Premium carrying case",
            "Bulk discount for 3+"
        ],
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

# Daily Report Routes
@api_router.get("/reports/daily", response_model=DailyReport)
async def get_daily_report(user: User = Depends(get_current_user)):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report = await db.daily_reports.find_one({"user_id": user.id, "date": today}, {"_id": 0})
    
    if not report:
        # Generate a new report
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

# Product Boards Routes
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

# Filter Settings Routes
@api_router.get("/settings/filters", response_model=FilterSettings)
async def get_filter_settings(user: User = Depends(get_current_user)):
    if user.filters:
        return FilterSettings(**user.filters)
    return FilterSettings()

@api_router.put("/settings/filters", response_model=FilterSettings)
async def update_filter_settings(filters: FilterSettings, user: User = Depends(get_current_user)):
    await db.users.update_one({"id": user.id}, {"$set": {"filters": filters.model_dump()}})
    return filters

# Categories
@api_router.get("/categories")
async def get_categories(user: User = Depends(get_current_user)):
    categories = await db.products.distinct("category")
    return categories

# Stats
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

# Seed data endpoint (for demo purposes)
@api_router.post("/seed")
async def seed_data():
    # Check if already seeded
    count = await db.products.count_documents({})
    if count > 0:
        return {"message": "Data already seeded", "count": count}
    
    sample_products = [
        Product(
            name="Portable Neck Fan",
            category="Electronics",
            image_url="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
            description="Rechargeable bladeless neck fan with 3 speed settings. Perfect for outdoor activities.",
            source_cost=6.20,
            recommended_price=34.99,
            margin_percent=72,
            suppliers=[
                Supplier(name="TechGadgets Store", platform="aliexpress", unit_cost=6.20, shipping_cost=2.30, shipping_days="12-18", rating=4.8, total_orders=12400),
                Supplier(name="CJ Dropshipping", platform="cj", unit_cost=7.50, shipping_cost=4.50, shipping_days="5-8", rating=4.7, total_orders=8500)
            ],
            overall_score=94,
            trend_score=95,
            competition_score=90,
            profit_score=92,
            trend_direction="up",
            trend_percent=340,
            search_volume=125000,
            active_fb_ads=18,
            shopify_stores=45,
            saturation_level="low",
            source_platforms=["tiktok", "amazon", "google_trends"]
        ),
        Product(
            name="LED Book Lamp",
            category="Home & Garden",
            image_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400",
            description="Wooden folding book lamp with warm LED light. Unique gift idea.",
            source_cost=11.40,
            recommended_price=44.99,
            margin_percent=68,
            suppliers=[
                Supplier(name="HomeDecor Factory", platform="aliexpress", unit_cost=11.40, shipping_cost=3.20, shipping_days="14-20", rating=4.6, total_orders=7800),
                Supplier(name="1688 Direct", platform="1688", unit_cost=8.50, shipping_cost=5.00, shipping_days="18-25", rating=4.5, total_orders=15000)
            ],
            overall_score=89,
            trend_score=85,
            competition_score=82,
            profit_score=88,
            trend_direction="up",
            trend_percent=180,
            search_volume=89000,
            active_fb_ads=34,
            shopify_stores=62,
            saturation_level="medium",
            source_platforms=["pinterest", "amazon"]
        ),
        Product(
            name="Cloud Slides",
            category="Fashion",
            image_url="https://images.unsplash.com/photo-1603808033192-082d6919d3e1?w=400",
            description="Ultra-soft pillow slides with thick sole. Comfort meets style.",
            source_cost=8.90,
            recommended_price=38.99,
            margin_percent=65,
            suppliers=[
                Supplier(name="FashionWear Co", platform="aliexpress", unit_cost=8.90, shipping_cost=2.80, shipping_days="10-15", rating=4.7, total_orders=25000),
                Supplier(name="Spocket US", platform="spocket", unit_cost=12.00, shipping_cost=0, shipping_days="3-5", rating=4.9, total_orders=3200)
            ],
            overall_score=86,
            trend_score=92,
            competition_score=70,
            profit_score=85,
            trend_direction="up",
            trend_percent=95,
            search_volume=210000,
            active_fb_ads=42,
            shopify_stores=120,
            saturation_level="medium",
            source_platforms=["tiktok", "google_trends"]
        ),
        Product(
            name="Mini Projector",
            category="Electronics",
            image_url="https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=400",
            description="Portable HD projector with WiFi. Transform any wall into a cinema.",
            source_cost=45.00,
            recommended_price=129.99,
            margin_percent=58,
            suppliers=[
                Supplier(name="ElectroHub", platform="aliexpress", unit_cost=45.00, shipping_cost=8.00, shipping_days="15-20", rating=4.5, total_orders=9200),
                Supplier(name="Alibaba Wholesale", platform="alibaba", unit_cost=38.00, shipping_cost=12.00, shipping_days="20-30", rating=4.4, total_orders=50000)
            ],
            overall_score=82,
            trend_score=78,
            competition_score=75,
            profit_score=80,
            trend_direction="stable",
            trend_percent=15,
            search_volume=340000,
            active_fb_ads=85,
            shopify_stores=200,
            saturation_level="high",
            source_platforms=["amazon", "aliexpress"]
        ),
        Product(
            name="Posture Corrector",
            category="Health & Wellness",
            image_url="https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400",
            description="Adjustable back brace for improved posture. Comfortable all-day wear.",
            source_cost=5.50,
            recommended_price=29.99,
            margin_percent=75,
            suppliers=[
                Supplier(name="HealthFirst", platform="aliexpress", unit_cost=5.50, shipping_cost=1.80, shipping_days="12-16", rating=4.6, total_orders=18000),
                Supplier(name="CJ Health", platform="cj", unit_cost=6.20, shipping_cost=3.50, shipping_days="6-9", rating=4.8, total_orders=5600)
            ],
            overall_score=79,
            trend_score=65,
            competition_score=72,
            profit_score=88,
            trend_direction="down",
            trend_percent=-12,
            search_volume=156000,
            active_fb_ads=95,
            shopify_stores=180,
            saturation_level="high",
            source_platforms=["amazon", "google_trends"]
        ),
        Product(
            name="Magnetic Phone Mount",
            category="Electronics",
            image_url="https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=400",
            description="360° rotating magnetic car mount. Works with MagSafe and all phones.",
            source_cost=4.20,
            recommended_price=24.99,
            margin_percent=78,
            suppliers=[
                Supplier(name="AutoAccessories", platform="aliexpress", unit_cost=4.20, shipping_cost=1.50, shipping_days="10-14", rating=4.7, total_orders=32000),
            ],
            overall_score=85,
            trend_score=80,
            competition_score=85,
            profit_score=90,
            trend_direction="up",
            trend_percent=45,
            search_volume=98000,
            active_fb_ads=28,
            shopify_stores=55,
            saturation_level="low",
            source_platforms=["amazon", "aliexpress"]
        ),
        Product(
            name="Smart Water Bottle",
            category="Health & Wellness",
            image_url="https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400",
            description="LED temperature display water bottle with reminder to drink.",
            source_cost=7.80,
            recommended_price=32.99,
            margin_percent=70,
            suppliers=[
                Supplier(name="SmartLife Store", platform="aliexpress", unit_cost=7.80, shipping_cost=2.40, shipping_days="12-18", rating=4.5, total_orders=8900),
            ],
            overall_score=88,
            trend_score=88,
            competition_score=85,
            profit_score=86,
            trend_direction="up",
            trend_percent=120,
            search_volume=67000,
            active_fb_ads=22,
            shopify_stores=38,
            saturation_level="low",
            source_platforms=["tiktok", "amazon"]
        ),
        Product(
            name="Sunset Lamp Projector",
            category="Home & Garden",
            image_url="https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=400",
            description="USB sunset projection lamp. Creates aesthetic room ambiance.",
            source_cost=6.50,
            recommended_price=28.99,
            margin_percent=72,
            suppliers=[
                Supplier(name="LightingWorld", platform="aliexpress", unit_cost=6.50, shipping_cost=2.00, shipping_days="10-15", rating=4.8, total_orders=45000),
            ],
            overall_score=91,
            trend_score=94,
            competition_score=88,
            profit_score=90,
            trend_direction="up",
            trend_percent=280,
            search_volume=185000,
            active_fb_ads=35,
            shopify_stores=78,
            saturation_level="medium",
            source_platforms=["tiktok", "pinterest", "google_trends"]
        )
    ]
    
    for product in sample_products:
        doc = product.model_dump()
        doc['discovered_at'] = doc['discovered_at'].isoformat()
        doc['last_updated'] = doc['last_updated'].isoformat()
        await db.products.insert_one(doc)
    
    return {"message": "Seeded successfully", "count": len(sample_products)}

# Health check
@api_router.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
