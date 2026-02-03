"""User management routes"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel

from models import User, UserResponse
from routes.deps import get_db, get_current_user
from routes.tiers import get_all_features_status, get_tier_limits, TIER_LEVELS

router = APIRouter(prefix="/user", tags=["user"])

class UserKeysUpdate(BaseModel):
    openai_api_key: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None

@router.get("/keys")
async def get_user_keys(user: User = Depends(get_current_user)):
    """Get user's API key configuration status (not the actual keys)"""
    return {
        "has_openai_key": bool(user.openai_api_key),
        "has_telegram_token": bool(user.telegram_bot_token),
        "telegram_chat_id": user.telegram_chat_id,
        "openai_key_masked": f"sk-...{user.openai_api_key[-4:]}" if user.openai_api_key else None,
        "telegram_token_masked": f"...{user.telegram_bot_token[-6:]}" if user.telegram_bot_token else None
    }

@router.put("/keys")
async def update_user_keys(keys: UserKeysUpdate, user: User = Depends(get_current_user)):
    """Update user's API keys"""
    db = get_db()
    update_data = {}
    
    if keys.openai_api_key is not None:
        update_data["openai_api_key"] = keys.openai_api_key if keys.openai_api_key else None
    if keys.telegram_bot_token is not None:
        update_data["telegram_bot_token"] = keys.telegram_bot_token if keys.telegram_bot_token else None
    if keys.telegram_chat_id is not None:
        update_data["telegram_chat_id"] = keys.telegram_chat_id if keys.telegram_chat_id else None
    
    if update_data:
        await db.users.update_one({"id": user.id}, {"$set": update_data})
    
    return {"success": True, "updated_fields": list(update_data.keys())}

@router.delete("/keys/{key_type}")
async def delete_user_key(key_type: str, user: User = Depends(get_current_user)):
    """Delete a specific API key"""
    db = get_db()
    valid_keys = ["openai_api_key", "telegram_bot_token", "telegram_chat_id"]
    if key_type not in valid_keys:
        raise HTTPException(status_code=400, detail=f"Invalid key type. Must be one of: {valid_keys}")
    
    await db.users.update_one({"id": user.id}, {"$set": {key_type: None}})
    return {"success": True, "deleted": key_type}

@router.get("/tier-status")
async def get_tier_status(user: User = Depends(get_current_user)):
    """Get user's tier status and available features"""
    return {
        "current_tier": user.subscription_tier,
        "tier_level": TIER_LEVELS.get(user.subscription_tier, 0),
        "limits": get_tier_limits(user.subscription_tier),
        "features": get_all_features_status(user.subscription_tier)
    }
