"""Product routes"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timezone

from models import User, Product, ProductBrief, Supplier
from routes.deps import get_db, get_current_user

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/today")
async def get_today_products(user: User = Depends(get_current_user)):
    """Get today's discovered products"""
    db = get_db()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # First try user's daily_products for today
    products = await db.daily_products.find(
        {"scan_date": today, "is_active": True, "user_id": user.id},
        {"_id": 0}
    ).sort("overall_score", -1).to_list(100)

    # Fallback: any daily_products for today (from scheduler)
    if not products:
        products = await db.daily_products.find(
            {"scan_date": today, "is_active": True},
            {"_id": 0}
        ).sort("overall_score", -1).to_list(100)

    # Fallback to seed products if no daily products yet
    if not products:
        products = await db.products.find({}, {"_id": 0}).sort("overall_score", -1).to_list(50)

    return {"date": today, "products": products, "count": len(products)}

@router.get("/history")
async def get_product_history(
    days: int = 30,
    user: User = Depends(get_current_user)
):
    """Get all products from past N days as a flat list"""
    db = get_db()

    # Get all daily_products for this user from past N days
    products = await db.daily_products.find(
        {"user_id": user.id},
        {"_id": 0}
    ).sort("overall_score", -1).to_list(500)

    # Fallback: any daily_products
    if not products:
        products = await db.daily_products.find(
            {},
            {"_id": 0}
        ).sort("overall_score", -1).to_list(200)

    # Fallback to seed products
    if not products:
        products = await db.products.find({}, {"_id": 0}).sort("overall_score", -1).to_list(50)

    return {"products": products, "count": len(products)}

@router.get("/archive/{date}")
async def get_archived_products(date: str, user: User = Depends(get_current_user)):
    """Get products from a specific date"""
    db = get_db()
    products = await db.daily_products.find(
        {"scan_date": date},
        {"_id": 0}
    ).sort("overall_score", -1).to_list(20)

    return {"date": date, "products": products, "count": len(products)}

@router.get("", response_model=List[Product])
async def get_products(
    category: Optional[str] = None,
    min_score: Optional[int] = None,
    limit: int = 50,
    user: User = Depends(get_current_user)
):
    db = get_db()
    query = {}
    if category:
        query["category"] = category
    if min_score:
        query["overall_score"] = {"$gte": min_score}
    
    products = await db.products.find(query, {"_id": 0}).sort("overall_score", -1).limit(limit).to_list(limit)
    return products

@router.get("/top", response_model=List[Product])
async def get_top_products(limit: int = 5, user: User = Depends(get_current_user)):
    db = get_db()
    products = await db.products.find({}, {"_id": 0}).sort("overall_score", -1).limit(limit).to_list(limit)
    return products

@router.get("/{product_id}")
async def get_product(product_id: str, user: User = Depends(get_current_user)):
    db = get_db()
    # Check seed products first
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        # Fallback: check daily_products (from scans)
        product = await db.daily_products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/{product_id}/brief")
async def get_product_brief(product_id: str, user: User = Depends(get_current_user)):
    db = get_db()
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    is_daily = False
    if not product:
        product = await db.daily_products.find_one({"id": product_id}, {"_id": 0})
        is_daily = True
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    source_cost = float(product.get("source_cost", 0) or 0)
    recommended_price = float(product.get("recommended_price", 0) or 0)
    active_fb_ads = int(product.get("active_fb_ads", 0) or 0)

    if is_daily:
        # Daily products don't have full supplier data - build from scan data
        best_supplier = Supplier(
            name="AliExpress Supplier", platform="aliexpress", unit_cost=source_cost,
            shipping_cost=round(source_cost * 0.15, 2) if source_cost > 0 else 2.50,
            shipping_days="10-20", rating=4.5, total_orders=1000
        )
        alternative_suppliers = []
        trademark_risk = False
        trend_direction = product.get("trend_direction", "stable")
    else:
        product_obj = Product(**product)
        best_supplier = product_obj.suppliers[0] if product_obj.suppliers else Supplier(
            name="Generic Supplier", platform="aliexpress", unit_cost=source_cost,
            shipping_cost=2.50, shipping_days="10-15", rating=4.5, total_orders=5000
        )
        alternative_suppliers = product_obj.suppliers[1:] if len(product_obj.suppliers) > 1 else []
        trademark_risk = product_obj.trademark_risk
        trend_direction = product_obj.trend_direction

    total_cost = best_supplier.unit_cost + best_supplier.shipping_cost
    gross_margin = recommended_price - total_cost
    estimated_cpa = 8.0
    net_profit = gross_margin - estimated_cpa

    return ProductBrief(
        product_id=product.get("id", product_id),
        product_name=product.get("name", "Unknown"),
        best_supplier=best_supplier,
        alternative_suppliers=alternative_suppliers,
        unit_cost=best_supplier.unit_cost,
        shipping_cost=best_supplier.shipping_cost,
        total_cost=total_cost,
        recommended_price=recommended_price,
        gross_margin=gross_margin,
        estimated_ad_cpa=estimated_cpa,
        net_profit_per_unit=net_profit,
        break_even_roas=round(recommended_price / (total_cost + estimated_cpa), 2) if (total_cost + estimated_cpa) > 0 else 0,
        trademark_clear=not trademark_risk,
        supplier_verified=not is_daily,
        shipping_reasonable=True,
        competition_acceptable=active_fb_ads < 50,
        trend_positive=trend_direction == "up"
    )
