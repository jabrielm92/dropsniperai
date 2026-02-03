"""Authentication routes"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone, timedelta
import jwt
import hashlib
import os

from models import User, UserCreate, UserLogin, UserResponse, TokenResponse
from routes.deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

# Admin email from environment
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'jabriel@arisolutionsinc.com')

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(user_id: str, secret: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }
    return jwt.encode(payload, secret, algorithm="HS256")

@router.post("/register", response_model=TokenResponse)
async def register(data: UserCreate):
    db = get_db()
    from routes.deps import JWT_SECRET
    
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    is_admin = data.email.lower() == ADMIN_EMAIL.lower()
    
    user = User(
        email=data.email,
        name=data.name,
        password_hash=hash_password(data.password),
        is_admin=is_admin
    )
    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.users.insert_one(doc)
    
    token = create_token(user.id, JWT_SECRET)
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id, 
            email=user.email, 
            name=user.name, 
            subscription_tier=user.subscription_tier,
            is_admin=user.is_admin
        )
    )

@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    db = get_db()
    from routes.deps import JWT_SECRET
    
    user_doc = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user_doc or user_doc['password_hash'] != hash_password(data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user_doc['id'], JWT_SECRET)
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user_doc['id'],
            email=user_doc['email'],
            name=user_doc['name'],
            subscription_tier=user_doc.get('subscription_tier', 'free'),
            is_admin=user_doc.get('is_admin', False),
            has_openai_key=bool(user_doc.get('openai_api_key')),
            has_telegram_token=bool(user_doc.get('telegram_bot_token')),
            telegram_chat_id=user_doc.get('telegram_chat_id')
        )
    )

@router.get("/me", response_model=UserResponse)
async def get_me():
    from fastapi import Depends
    from routes.deps import get_current_user
    # This will be handled by the dependency
    pass
