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

    # First try daily_products collection
    products = await db.daily_products.find(
        {"scan_date": today, "is_active": True},
        {"_id": 0}
    ).sort("overall_score", -1).limit(5).to_list(5)

    # Fallback to seed products if no daily products yet
    if not products:
        products = await db.products.find({}, {"_id": 0}).sort("overall_score", -1).limit(5).to_list(5)

    return {"date": today, "products": products, "count": len(products)}

@router.get("/history")
async def get_product_history(
    days: int = 30,
    user: User = Depends(get_current_user)
):
    """Get archived products from past days"""
    db = get_db()
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

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str, user: User = Depends(get_current_user)):
    db = get_db()
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/{product_id}/brief", response_model=ProductBrief)
async def get_product_brief(product_id: str, user: User = Depends(get_current_user)):
    db = get_db()
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
