"""Stripe payment routes"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
import stripe
import os
from datetime import datetime, timezone

from models import User
from routes.deps import get_db, get_current_user

router = APIRouter(prefix="/payments", tags=["payments"])

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

PRICE_IDS = {
    "scout": "price_scout_monthly",
    "hunter": "price_hunter_monthly",
    "predator": "price_predator_monthly",
    "agency": "price_agency_monthly"
}

TIER_PRICES = {
    "scout": 2900,      # $29/month
    "hunter": 7900,     # $79/month
    "predator": 14900,  # $149/month
    "agency": 29900     # $299/month
}

class CreateCheckoutRequest(BaseModel):
    tier: str
    success_url: str
    cancel_url: str

class SubscriptionUpdate(BaseModel):
    new_tier: str

@router.post("/create-checkout")
async def create_checkout_session(
    request: CreateCheckoutRequest,
    user: User = Depends(get_current_user)
):
    """Create a Stripe checkout session for subscription"""
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    if request.tier not in TIER_PRICES:
        raise HTTPException(status_code=400, detail="Invalid subscription tier")
    
    try:
        # Create or get Stripe customer
        db = get_db()
        user_doc = await db.users.find_one({"id": user.id})
        
        if user_doc.get("stripe_customer_id"):
            customer_id = user_doc["stripe_customer_id"]
        else:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.name,
                metadata={"user_id": user.id}
            )
            customer_id = customer.id
            await db.users.update_one(
                {"id": user.id},
                {"$set": {"stripe_customer_id": customer_id}}
            )
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"ProductScout AI - {request.tier.title()} Plan",
                        "description": f"Monthly subscription to {request.tier.title()} tier"
                    },
                    "unit_amount": TIER_PRICES[request.tier],
                    "recurring": {"interval": "month"}
                },
                "quantity": 1
            }],
            mode="subscription",
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata={
                "user_id": user.id,
                "tier": request.tier
            }
        )
        
        return {"checkout_url": session.url, "session_id": session.id}
        
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    db = get_db()
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["metadata"]["user_id"]
        tier = session["metadata"]["tier"]
        
        await db.users.update_one(
            {"id": user_id},
            {
                "$set": {
                    "subscription_tier": tier,
                    "stripe_subscription_id": session.get("subscription"),
                    "subscription_updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
    
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]
        
        await db.users.update_one(
            {"stripe_customer_id": customer_id},
            {
                "$set": {
                    "subscription_tier": "free",
                    "stripe_subscription_id": None,
                    "subscription_updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
    
    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        customer_id = invoice["customer"]
        
        # Could send notification to user about failed payment
        await db.payment_events.insert_one({
            "type": "payment_failed",
            "customer_id": customer_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    return {"status": "success"}

@router.get("/subscription")
async def get_subscription_status(user: User = Depends(get_current_user)):
    """Get current subscription status"""
    db = get_db()
    user_doc = await db.users.find_one({"id": user.id}, {"_id": 0})
    
    return {
        "tier": user_doc.get("subscription_tier", "free"),
        "stripe_customer_id": user_doc.get("stripe_customer_id"),
        "subscription_id": user_doc.get("stripe_subscription_id"),
        "updated_at": user_doc.get("subscription_updated_at")
    }

@router.post("/portal")
async def create_portal_session(user: User = Depends(get_current_user)):
    """Create Stripe customer portal session for managing subscription"""
    db = get_db()
    user_doc = await db.users.find_one({"id": user.id})
    
    if not user_doc.get("stripe_customer_id"):
        raise HTTPException(status_code=400, detail="No subscription found")
    
    try:
        session = stripe.billing_portal.Session.create(
            customer=user_doc["stripe_customer_id"],
            return_url=os.environ.get("FRONTEND_URL", "http://localhost:3000") + "/settings"
        )
        return {"portal_url": session.url}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
