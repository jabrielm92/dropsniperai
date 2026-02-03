"""Product routes"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timezone

from models import User, Product, ProductBrief, Supplier
from routes.deps import get_db, get_current_user

router = APIRouter(prefix="/products", tags=["products"])

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
