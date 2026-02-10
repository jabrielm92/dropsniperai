from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid

# Auth Models
class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    password_hash: str
    subscription_tier: str = "free"
    is_admin: bool = False
    # User's own API keys (per-tenant)
    openai_api_key: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    filters: Optional[Dict[str, Any]] = None
    notification_preferences: Optional[Dict[str, Any]] = None

class NotificationPreferences(BaseModel):
    daily_report: bool = True
    competition_alerts: bool = True
    trend_spike_alerts: bool = True
    scan_complete: bool = True

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    subscription_tier: str
    is_admin: bool = False
    telegram_chat_id: Optional[str] = None
    has_openai_key: bool = False
    has_telegram_token: bool = False

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Supplier Model
class Supplier(BaseModel):
    name: str
    platform: str  # aliexpress, cj, 1688, alibaba
    unit_cost: float
    shipping_cost: float
    shipping_days: str
    rating: float
    total_orders: int
    url: Optional[str] = None

# Product Models
class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str
    image_url: Optional[str] = ""
    description: Optional[str] = None
    
    # Sourcing
    source_cost: float
    recommended_price: float
    margin_percent: float
    suppliers: List[Supplier] = []
    
    # Scores
    overall_score: int  # 0-100
    trend_score: int
    competition_score: int
    profit_score: int
    
    # Trends
    trend_direction: str  # up, down, stable
    trend_percent: float
    search_volume: int
    
    # Competition
    active_fb_ads: int
    shopify_stores: int
    saturation_level: str  # low, medium, high
    
    # Validation
    trademark_risk: bool = False
    can_demo_video: bool = True
    
    # Sources found
    source_platforms: List[str] = []  # tiktok, amazon, aliexpress, google_trends
    
    # Timestamps
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProductBrief(BaseModel):
    product_id: str
    product_name: str
    
    # Sourcing summary
    best_supplier: Supplier
    alternative_suppliers: List[Supplier]
    
    # Pricing breakdown
    unit_cost: float
    shipping_cost: float
    total_cost: float
    recommended_price: float
    gross_margin: float
    estimated_ad_cpa: float
    net_profit_per_unit: float
    break_even_roas: float
    
    # Validation checklist
    trademark_clear: bool
    supplier_verified: bool
    shipping_reasonable: bool
    competition_acceptable: bool
    trend_positive: bool

# Launch Kit Models
class AdCopy(BaseModel):
    style: str  # short, long, emoji, story, urgency
    headline: str
    body: str
    cta: str

class VideoScript(BaseModel):
    hook: str
    problem: str
    solution: str
    cta: str
    duration_seconds: int

class LaunchKit(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    user_id: str
    
    # Product info
    product_name: str
    product_description: str
    
    # Generated content
    ad_copies: List[AdCopy] = []
    video_scripts: List[VideoScript] = []
    target_audiences: List[str] = []
    hashtags: List[str] = []
    
    # Pricing
    pricing_tiers: Dict[str, float] = {}
    upsell_suggestions: List[str] = []
    
    # Checklist
    launch_checklist: List[Dict[str, Any]] = []
    
    # Status
    status: str = "draft"  # draft, ready, launched
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Daily Report Models
class DailyReport(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    date: str
    
    # Scan stats
    products_scanned: int
    passed_filters: int
    fully_validated: int
    ready_to_launch: int
    
    # Top opportunities
    top_products: List[str] = []  # product IDs
    
    # Alerts
    alerts: List[Dict[str, Any]] = []
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Saved Products / Boards
class ProductBoard(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    description: Optional[str] = None
    product_ids: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Filter Settings
class FilterSettings(BaseModel):
    max_source_cost: float = 15.0
    min_sell_price: float = 35.0
    min_margin_percent: float = 60.0
    max_fb_ads: int = 50
    max_shipping_days: int = 15
    categories: List[str] = []
    exclude_trademark_risk: bool = True
