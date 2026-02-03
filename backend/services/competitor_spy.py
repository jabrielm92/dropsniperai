"""
Competitor Spy Service - Monitor competitor stores
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import uuid
import hashlib


class CompetitorStore(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    store_url: str
    store_name: str
    platform: str = "shopify"  # shopify, woocommerce, etc.
    last_scanned: Optional[datetime] = None
    products_snapshot: List[str] = []  # Product names from last scan
    new_products_count: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CompetitorAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    competitor_id: str
    competitor_name: str
    alert_type: str  # new_product, price_change, store_update
    title: str
    message: str
    product_data: Optional[Dict[str, Any]] = None
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CompetitorProduct(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    competitor_id: str
    name: str
    price: float
    url: Optional[str] = None
    image_url: Optional[str] = None
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    price_history: List[Dict[str, Any]] = []
    is_active: bool = True


def generate_mock_competitor_data(store_url: str) -> Dict[str, Any]:
    """Generate realistic mock data for a competitor store"""
    store_id = hashlib.md5(store_url.encode()).hexdigest()[:8]
    store_name = store_url.replace("https://", "").replace("http://", "").split(".")[0].title()
    
    # Sample trending products that competitors might sell
    product_pool = [
        {"name": "Portable Neck Fan Pro", "price": 34.99, "category": "Electronics"},
        {"name": "LED Galaxy Projector", "price": 49.99, "category": "Home"},
        {"name": "Cloud Comfort Slides", "price": 29.99, "category": "Fashion"},
        {"name": "Smart Posture Trainer", "price": 39.99, "category": "Health"},
        {"name": "Mini Waffle Maker", "price": 24.99, "category": "Kitchen"},
        {"name": "Wireless Charging Station", "price": 44.99, "category": "Electronics"},
        {"name": "Sunset Mood Lamp", "price": 27.99, "category": "Home"},
        {"name": "Ice Roller Set", "price": 19.99, "category": "Beauty"},
        {"name": "Magnetic Phone Ring", "price": 14.99, "category": "Accessories"},
        {"name": "UV Sanitizer Box", "price": 32.99, "category": "Health"},
        {"name": "Foldable Laptop Stand", "price": 28.99, "category": "Office"},
        {"name": "Smart Jump Rope", "price": 36.99, "category": "Fitness"},
    ]
    
    import random
    selected_products = random.sample(product_pool, random.randint(5, 10))
    
    return {
        "store_id": store_id,
        "store_name": store_name,
        "store_url": store_url,
        "products": selected_products,
        "total_products": len(selected_products),
        "estimated_monthly_revenue": random.randint(10000, 150000),
        "top_category": max(set(p["category"] for p in selected_products), 
                          key=lambda x: sum(1 for p in selected_products if p["category"] == x)),
        "avg_price": round(sum(p["price"] for p in selected_products) / len(selected_products), 2),
        "last_updated": datetime.now(timezone.utc).isoformat()
    }


def detect_store_changes(old_products: List[str], new_products: List[Dict]) -> Dict[str, Any]:
    """Detect changes between two snapshots of a store"""
    old_set = set(old_products)
    new_set = {p["name"] for p in new_products}
    
    added = new_set - old_set
    removed = old_set - new_set
    
    return {
        "added_products": list(added),
        "removed_products": list(removed),
        "added_count": len(added),
        "removed_count": len(removed),
        "has_changes": len(added) > 0 or len(removed) > 0
    }
