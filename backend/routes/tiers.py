"""Tier-based feature gating middleware"""
from fastapi import HTTPException
from models import User

# Tier hierarchy (higher number = more access)
TIER_LEVELS = {
    "free": 0,
    "sniper": 1,
    "elite": 2,
    "agency": 3,
    "enterprise": 4
}

# Feature requirements
FEATURE_TIERS = {
    "basic_products": "free",
    "daily_report": "free",
    "launch_kit": "sniper",
    "telegram_alerts": "elite",
    "competitor_spy": "elite",
    "saturation_radar": "elite",
    "export_shopify": "elite",
    "export_woocommerce": "elite",
    "google_trends": "elite",
    "unlimited_products": "elite",
    "api_access": "agency",
    "team_seats": "agency",
    "white_label": "agency"
}

# Daily limits per tier
TIER_LIMITS = {
    "free": {"products_per_day": 3, "scans_per_day": 1, "competitors": 0},
    "sniper": {"products_per_day": 10, "scans_per_day": 3, "competitors": 2},
    "elite": {"products_per_day": -1, "scans_per_day": -1, "competitors": 10},  # -1 = unlimited
    "agency": {"products_per_day": -1, "scans_per_day": -1, "competitors": -1},
    "enterprise": {"products_per_day": -1, "scans_per_day": -1, "competitors": -1}
}

def get_tier_level(tier: str) -> int:
    return TIER_LEVELS.get(tier, 0)

def has_feature_access(user: User, feature: str) -> bool:
    """Check if user's tier has access to a feature"""
    required_tier = FEATURE_TIERS.get(feature, "free")
    user_level = get_tier_level(user.subscription_tier)
    required_level = get_tier_level(required_tier)
    return user_level >= required_level

def require_feature(feature: str):
    """Decorator to require a specific feature tier"""
    def check_access(user: User):
        if not has_feature_access(user, feature):
            required = FEATURE_TIERS.get(feature, "elite")
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "upgrade_required",
                    "feature": feature,
                    "required_tier": required,
                    "current_tier": user.subscription_tier,
                    "message": f"Upgrade to {required.title()} to access this feature"
                }
            )
        return user
    return check_access

def get_tier_limits(tier: str) -> dict:
    """Get limits for a tier"""
    return TIER_LIMITS.get(tier, TIER_LIMITS["free"])

def get_all_features_status(user: User) -> dict:
    """Get status of all features for a user"""
    return {
        feature: {
            "available": has_feature_access(user, feature),
            "required_tier": tier
        }
        for feature, tier in FEATURE_TIERS.items()
    }
