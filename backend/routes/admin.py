"""Admin routes"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional

from models import User
from routes.deps import get_db, require_admin

router = APIRouter(prefix="/admin", tags=["admin"])

class CreateUserRequest(BaseModel):
    email: str
    name: str
    password: str
    subscription_tier: str = "free"

class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    subscription_tier: Optional[str] = None
    is_admin: Optional[bool] = None

@router.get("/stats")
async def get_admin_stats(admin: User = Depends(require_admin)):
    """Get platform-wide statistics"""
    db = get_db()
    total_users = await db.users.count_documents({})
    paid_users = await db.users.count_documents({"subscription_tier": {"$ne": "free"}})
    free_users = await db.users.count_documents({"subscription_tier": "free"})
    users_with_openai = await db.users.count_documents({"openai_api_key": {"$ne": None}})
    users_with_telegram = await db.users.count_documents({"telegram_bot_token": {"$ne": None}})
    total_products = await db.products.count_documents({})
    total_daily_products = await db.daily_products.count_documents({})
    total_scans = await db.scan_history.count_documents({})
    total_launch_kits = await db.launch_kits.count_documents({})
    total_competitors = await db.competitors.count_documents({})
    
    # Tier breakdown
    tier_counts = {}
    for tier in ["free", "sniper", "elite", "agency", "enterprise"]:
        tier_counts[tier] = await db.users.count_documents({"subscription_tier": tier})
    
    return {
        "total_users": total_users,
        "paid_users": paid_users,
        "free_users": free_users,
        "users_with_openai": users_with_openai,
        "users_with_telegram": users_with_telegram,
        "total_products": total_products,
        "total_daily_products": total_daily_products,
        "total_scans": total_scans,
        "total_launch_kits": total_launch_kits,
        "total_competitors": total_competitors,
        "tier_breakdown": tier_counts
    }

@router.get("/users")
async def get_admin_users(skip: int = 0, limit: int = 50, admin: User = Depends(require_admin)):
    """Get all users with their details"""
    db = get_db()
    users = await db.users.find(
        {}, 
        {"_id": 0, "password_hash": 0, "openai_api_key": 0, "telegram_bot_token": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    total = await db.users.count_documents({})
    
    # Add payment status placeholder (would integrate with Stripe)
    for user in users:
        user["has_openai_key"] = bool(await db.users.find_one({"id": user["id"], "openai_api_key": {"$ne": None}}))
        user["has_telegram"] = bool(await db.users.find_one({"id": user["id"], "telegram_bot_token": {"$ne": None}}))
    
    return {"users": users, "total": total, "skip": skip, "limit": limit}

@router.get("/users/{user_id}")
async def get_admin_user_detail(user_id: str, admin: User = Depends(require_admin)):
    """Get detailed info for a specific user"""
    db = get_db()
    user = await db.users.find_one(
        {"id": user_id}, 
        {"_id": 0, "password_hash": 0, "openai_api_key": 0, "telegram_bot_token": 0}
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's activity
    scan_count = await db.scan_history.count_documents({"user_id": user_id})
    launch_kit_count = await db.launch_kits.count_documents({"user_id": user_id})
    
    # Check integrations
    full_user = await db.users.find_one({"id": user_id}, {"_id": 0})
    user["has_openai_key"] = bool(full_user.get("openai_api_key"))
    user["has_telegram"] = bool(full_user.get("telegram_bot_token"))
    user["telegram_chat_id"] = full_user.get("telegram_chat_id")
    user["free_report_sent"] = full_user.get("free_report_sent", False)
    user["last_scan_at"] = full_user.get("last_scan_at")
    user["scan_count"] = scan_count
    user["launch_kit_count"] = launch_kit_count
    
    return user

@router.post("/users")
async def create_admin_user(data: CreateUserRequest, admin: User = Depends(require_admin)):
    """Create a new user (admin only)"""
    from routes.auth import hash_password
    import uuid
    db = get_db()

    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    valid_tiers = ["free", "sniper", "elite", "agency", "enterprise"]
    if data.subscription_tier not in valid_tiers:
        raise HTTPException(status_code=400, detail=f"Invalid tier. Must be one of: {valid_tiers}")

    user_doc = {
        "id": str(uuid.uuid4()),
        "email": data.email,
        "name": data.name,
        "password_hash": hash_password(data.password),
        "subscription_tier": data.subscription_tier,
        "is_admin": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(user_doc)
    
    return {"success": True, "user_id": user_doc["id"], "email": data.email}

@router.put("/users/{user_id}")
async def update_admin_user(user_id: str, data: UpdateUserRequest, admin: User = Depends(require_admin)):
    """Update a user's details"""
    db = get_db()
    
    update_data = {}
    if data.name is not None:
        update_data["name"] = data.name
    if data.subscription_tier is not None:
        valid_tiers = ["free", "sniper", "elite", "agency", "enterprise"]
        if data.subscription_tier not in valid_tiers:
            raise HTTPException(status_code=400, detail=f"Invalid tier. Must be one of: {valid_tiers}")
        update_data["subscription_tier"] = data.subscription_tier
        # Reset free report flag if upgrading from free
        if data.subscription_tier != "free":
            update_data["free_report_sent"] = False
    if data.is_admin is not None:
        update_data["is_admin"] = data.is_admin
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    result = await db.users.update_one({"id": user_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"success": True, "user_id": user_id, "updated_fields": list(update_data.keys())}

@router.put("/users/{user_id}/tier")
async def update_user_tier(user_id: str, tier: str, admin: User = Depends(require_admin)):
    """Update a user's subscription tier"""
    db = get_db()
    valid_tiers = ["free", "sniper", "elite", "agency", "enterprise"]
    if tier not in valid_tiers:
        raise HTTPException(status_code=400, detail=f"Invalid tier. Must be one of: {valid_tiers}")
    
    update_data = {"subscription_tier": tier}
    # Reset free report flag if upgrading
    if tier != "free":
        update_data["free_report_sent"] = False
    
    result = await db.users.update_one({"id": user_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"success": True, "user_id": user_id, "new_tier": tier}

@router.delete("/users/{user_id}")
async def delete_admin_user(user_id: str, admin: User = Depends(require_admin)):
    """Delete a user"""
    db = get_db()
    
    # Don't allow deleting yourself
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Clean up user's data
    await db.scan_history.delete_many({"user_id": user_id})
    await db.launch_kits.delete_many({"user_id": user_id})
    await db.daily_products.delete_many({"user_id": user_id})
    await db.competitors.delete_many({"user_id": user_id})
    await db.boards.delete_many({"user_id": user_id})
    
    return {"success": True, "user_id": user_id, "message": "User and associated data deleted"}

@router.get("/activity")
async def get_recent_activity(limit: int = 20, admin: User = Depends(require_admin)):
    """Get recent platform activity"""
    db = get_db()
    recent_scans = await db.scan_history.find(
        {}, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    recent_launch_kits = await db.launch_kits.find(
        {}, {"_id": 0, "ad_copies": 0, "video_scripts": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    recent_signups = await db.users.find(
        {}, {"_id": 0, "password_hash": 0, "openai_api_key": 0, "telegram_bot_token": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return {
        "recent_scans": recent_scans,
        "recent_launch_kits": recent_launch_kits,
        "recent_signups": recent_signups
    }

@router.get("/scheduler/status")
async def get_scheduler_status(admin: User = Depends(require_admin)):
    """Get background scheduler status"""
    from services.scheduler import _scheduler
    
    if _scheduler is None:
        return {"running": False, "message": "Scheduler not initialized"}
    
    jobs = []
    for job in _scheduler.scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None
        })
    
    return {
        "running": _scheduler._running,
        "jobs": jobs
    }

@router.post("/scheduler/trigger-reports")
async def trigger_daily_reports(admin: User = Depends(require_admin)):
    """Manually trigger daily Telegram reports"""
    from services.scheduler import get_scheduler
    
    scheduler = get_scheduler(get_db())
    await scheduler.send_daily_reports()
    
    return {"success": True, "message": "Daily reports triggered"}

