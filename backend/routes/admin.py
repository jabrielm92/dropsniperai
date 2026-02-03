"""Admin routes"""
from fastapi import APIRouter, Depends
from datetime import datetime, timezone

from models import User
from routes.deps import get_db, require_admin

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats")
async def get_admin_stats(admin: User = Depends(require_admin)):
    """Get platform-wide statistics"""
    db = get_db()
    total_users = await db.users.count_documents({})
    paid_users = await db.users.count_documents({"subscription_tier": {"$ne": "free"}})
    users_with_openai = await db.users.count_documents({"openai_api_key": {"$ne": None}})
    users_with_telegram = await db.users.count_documents({"telegram_bot_token": {"$ne": None}})
    total_products = await db.products.count_documents({})
    total_scans = await db.scan_history.count_documents({})
    total_launch_kits = await db.launch_kits.count_documents({})
    total_competitors = await db.competitors.count_documents({})
    
    return {
        "total_users": total_users,
        "paid_users": paid_users,
        "users_with_openai": users_with_openai,
        "users_with_telegram": users_with_telegram,
        "total_products": total_products,
        "total_scans": total_scans,
        "total_launch_kits": total_launch_kits,
        "total_competitors": total_competitors
    }

@router.get("/users")
async def get_admin_users(skip: int = 0, limit: int = 50, admin: User = Depends(require_admin)):
    """Get all users with their details"""
    db = get_db()
    users = await db.users.find(
        {}, 
        {"_id": 0, "password_hash": 0}
    ).skip(skip).limit(limit).to_list(limit)
    
    total = await db.users.count_documents({})
    
    return {"users": users, "total": total, "skip": skip, "limit": limit}

@router.put("/users/{user_id}/tier")
async def update_user_tier(user_id: str, tier: str, admin: User = Depends(require_admin)):
    """Update a user's subscription tier"""
    db = get_db()
    valid_tiers = ["free", "scout", "hunter", "predator", "agency"]
    if tier not in valid_tiers:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Invalid tier. Must be one of: {valid_tiers}")
    
    result = await db.users.update_one({"id": user_id}, {"$set": {"subscription_tier": tier}})
    if result.matched_count == 0:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"success": True, "user_id": user_id, "new_tier": tier}

@router.get("/activity")
async def get_recent_activity(limit: int = 10, admin: User = Depends(require_admin)):
    """Get recent platform activity"""
    db = get_db()
    recent_scans = await db.scan_history.find(
        {}, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    recent_launch_kits = await db.launch_kits.find(
        {}, {"_id": 0, "ad_copies": 0, "video_scripts": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return {
        "recent_scans": recent_scans,
        "recent_launch_kits": recent_launch_kits
    }
