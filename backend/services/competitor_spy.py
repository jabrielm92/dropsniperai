"""
Competitor Spy Service - Real Shopify store monitoring via products.json
Tracks product additions, removals, price changes, and estimated revenue.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import uuid

import httpx

logger = logging.getLogger(__name__)


class CompetitorStore(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    store_url: str
    store_name: str
    platform: str = "shopify"
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


async def scrape_shopify_store(store_url: str) -> Dict[str, Any]:
    """Scrape a real Shopify store via its public products.json endpoint"""
    store_url = store_url.rstrip("/")
    if not store_url.startswith("http"):
        store_url = f"https://{store_url}"

    result = {
        "store_name": store_url.split("//")[-1].split(".")[0].title(),
        "store_url": store_url,
        "products": [],
        "total_products": 0,
        "estimated_monthly_revenue": 0,
        "top_category": "Unknown",
        "avg_price": 0,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    all_products = []

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        page = 1
        while page <= 10:  # Max 10 pages (300 products)
            try:
                url = f"{store_url}/products.json?page={page}&limit=250"
                resp = await client.get(url, headers=headers)

                if resp.status_code != 200:
                    if page == 1:
                        logger.warning(f"Cannot access {store_url}/products.json - status {resp.status_code}")
                    break

                data = resp.json()
                products = data.get("products", [])
                if not products:
                    break

                all_products.extend(products)
                page += 1

                if len(products) < 30:
                    break

            except Exception as e:
                logger.warning(f"Error fetching page {page} from {store_url}: {e}")
                break

        # Also try to get store name from the shop metadata
        try:
            meta_resp = await client.get(f"{store_url}/meta.json", headers=headers)
            if meta_resp.status_code == 200:
                meta = meta_resp.json()
                result["store_name"] = meta.get("name", result["store_name"])
        except Exception:
            pass

    # Process products
    categories = {}
    total_price = 0
    for p in all_products:
        variants = p.get("variants", [{}])
        prices = [float(v.get("price", "0")) for v in variants if v.get("price")]
        price = min(prices) if prices else 0
        category = p.get("product_type", "Uncategorized") or "Uncategorized"

        categories[category] = categories.get(category, 0) + 1
        total_price += price

        result["products"].append({
            "name": p.get("title", "Unknown"),
            "price": price,
            "category": category,
            "url": f"{store_url}/products/{p.get('handle', '')}",
            "image_url": (p.get("images", [{}])[0].get("src", "") if p.get("images") else ""),
            "created_at": p.get("created_at", ""),
            "updated_at": p.get("updated_at", ""),
            "vendor": p.get("vendor", ""),
            "tags": p.get("tags", []),
        })

    result["total_products"] = len(result["products"])
    if result["products"]:
        result["avg_price"] = round(total_price / len(result["products"]), 2)
        # Rough revenue estimate: avg_price * product_count * 30 sales/mo estimate
        # Conservative: assume each product gets ~1 sale/day
        result["estimated_monthly_revenue"] = round(result["avg_price"] * len(result["products"]) * 30, 0)
    if categories:
        result["top_category"] = max(categories, key=categories.get)

    return result


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
        "has_changes": len(added) > 0 or len(removed) > 0,
    }


def detect_price_changes(
    old_products: List[Dict[str, Any]],
    new_products: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Detect price changes between two product snapshots"""
    old_prices = {p["name"]: p.get("price", 0) for p in old_products}
    changes = []

    for p in new_products:
        name = p["name"]
        new_price = p.get("price", 0)
        old_price = old_prices.get(name)

        if old_price is not None and old_price != new_price and old_price > 0:
            change_pct = round(((new_price - old_price) / old_price) * 100, 1)
            changes.append({
                "name": name,
                "old_price": old_price,
                "new_price": new_price,
                "change_percent": change_pct,
                "direction": "up" if new_price > old_price else "down",
            })

    return changes
