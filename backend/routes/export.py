"""E-commerce export routes for Shopify and WooCommerce"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
import json
from datetime import datetime, timezone

from models import User, Product
from routes.deps import get_db, get_current_user

router = APIRouter(prefix="/export", tags=["export"])

class ExportConfig(BaseModel):
    product_ids: List[str]
    platform: str  # shopify or woocommerce
    include_images: bool = True
    include_description: bool = True
    price_markup: float = 1.0  # 1.0 = no markup, 1.2 = 20% markup

@router.post("/shopify")
async def export_to_shopify(
    config: ExportConfig,
    user: User = Depends(get_current_user)
):
    """Export products in Shopify CSV format"""
    db = get_db()
    
    products = await db.products.find(
        {"id": {"$in": config.product_ids}}, 
        {"_id": 0}
    ).to_list(100)
    
    if not products:
        raise HTTPException(status_code=404, detail="No products found")
    
    # Shopify CSV format
    shopify_products = []
    for p in products:
        product = Product(**p)
        price = product.recommended_price * config.price_markup
        
        shopify_products.append({
            "Handle": product.id,
            "Title": product.name,
            "Body (HTML)": f"<p>{product.description}</p>" if config.include_description else "",
            "Vendor": "ProductScout AI",
            "Product Category": product.category,
            "Type": product.category,
            "Tags": f"trending, {product.category.lower()}, productscout",
            "Published": "TRUE",
            "Option1 Name": "Title",
            "Option1 Value": "Default Title",
            "Variant SKU": f"PS-{product.id[:8]}",
            "Variant Grams": "0",
            "Variant Inventory Tracker": "shopify",
            "Variant Inventory Qty": "100",
            "Variant Inventory Policy": "deny",
            "Variant Fulfillment Service": "manual",
            "Variant Price": f"{price:.2f}",
            "Variant Compare At Price": f"{price * 1.3:.2f}",
            "Variant Requires Shipping": "TRUE",
            "Variant Taxable": "TRUE",
            "Image Src": product.image_url if config.include_images else "",
            "Image Position": "1",
            "Image Alt Text": product.name,
            "Gift Card": "FALSE",
            "SEO Title": f"{product.name} - Premium Quality",
            "SEO Description": product.description[:160] if product.description else "",
            "Variant Weight Unit": "kg",
            "Status": "draft"
        })
    
    # Log export
    await db.exports.insert_one({
        "user_id": user.id,
        "platform": "shopify",
        "product_count": len(shopify_products),
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "platform": "shopify",
        "format": "csv",
        "product_count": len(shopify_products),
        "products": shopify_products,
        "instructions": {
            "step1": "Go to Shopify Admin > Products > Import",
            "step2": "Download this data as CSV or copy to your import tool",
            "step3": "Upload the CSV file",
            "step4": "Review and publish products"
        }
    }

@router.post("/woocommerce")
async def export_to_woocommerce(
    config: ExportConfig,
    user: User = Depends(get_current_user)
):
    """Export products in WooCommerce format"""
    db = get_db()
    
    products = await db.products.find(
        {"id": {"$in": config.product_ids}}, 
        {"_id": 0}
    ).to_list(100)
    
    if not products:
        raise HTTPException(status_code=404, detail="No products found")
    
    # WooCommerce CSV format
    woo_products = []
    for p in products:
        product = Product(**p)
        price = product.recommended_price * config.price_markup
        
        woo_products.append({
            "ID": "",
            "Type": "simple",
            "SKU": f"PS-{product.id[:8]}",
            "Name": product.name,
            "Published": "0",  # Draft
            "Is featured?": "0",
            "Visibility in catalog": "visible",
            "Short description": product.description[:200] if product.description else "",
            "Description": f"<p>{product.description}</p>" if config.include_description else "",
            "Date sale price starts": "",
            "Date sale price ends": "",
            "Tax status": "taxable",
            "Tax class": "",
            "In stock?": "1",
            "Stock": "100",
            "Low stock amount": "10",
            "Backorders allowed?": "0",
            "Sold individually?": "0",
            "Weight (kg)": "",
            "Length (cm)": "",
            "Width (cm)": "",
            "Height (cm)": "",
            "Allow customer reviews?": "1",
            "Purchase note": "",
            "Sale price": f"{price * 0.85:.2f}",
            "Regular price": f"{price:.2f}",
            "Categories": product.category,
            "Tags": f"trending, {product.category.lower()}",
            "Shipping class": "",
            "Images": product.image_url if config.include_images else "",
            "Download limit": "",
            "Download expiry days": "",
            "Parent": "",
            "Grouped products": "",
            "Upsells": "",
            "Cross-sells": "",
            "External URL": "",
            "Button text": "",
            "Position": "0",
            "Meta: _source_cost": str(product.source_cost),
            "Meta: _margin_percent": str(product.margin_percent),
            "Meta: _productscout_id": product.id
        })
    
    # Log export
    await db.exports.insert_one({
        "user_id": user.id,
        "platform": "woocommerce",
        "product_count": len(woo_products),
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "platform": "woocommerce",
        "format": "csv",
        "product_count": len(woo_products),
        "products": woo_products,
        "instructions": {
            "step1": "Go to WooCommerce > Products > Import",
            "step2": "Download this data as CSV",
            "step3": "Upload the CSV and map columns",
            "step4": "Run the import and review products"
        }
    }

@router.get("/history")
async def get_export_history(user: User = Depends(get_current_user)):
    """Get user's export history"""
    db = get_db()
    exports = await db.exports.find(
        {"user_id": user.id}, 
        {"_id": 0}
    ).sort("created_at", -1).limit(20).to_list(20)
    
    return {"exports": exports}

@router.post("/download/{format}")
async def download_export(
    format: str,
    config: ExportConfig,
    user: User = Depends(get_current_user)
):
    """Generate downloadable CSV content"""
    if config.platform == "shopify":
        result = await export_to_shopify(config, user)
    elif config.platform == "woocommerce":
        result = await export_to_woocommerce(config, user)
    else:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    if format == "json":
        return result
    
    # Generate CSV string
    if result["products"]:
        headers = list(result["products"][0].keys())
        csv_lines = [",".join(f'"{h}"' for h in headers)]
        
        for product in result["products"]:
            values = [f'"{str(product.get(h, "")).replace(chr(34), chr(39))}"' for h in headers]
            csv_lines.append(",".join(values))
        
        csv_content = "\n".join(csv_lines)
        
        return {
            "csv_content": csv_content,
            "filename": f"{config.platform}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "product_count": len(result["products"])
        }
    
    return {"error": "No products to export"}
