"""Authentication routes"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
import jwt
import hashlib
import bcrypt
import os

from models import User, UserCreate, UserLogin, UserResponse, TokenResponse
from routes.deps import get_db, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

# Admin email from environment
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'jabriel@arisolutionsinc.com')

def hash_password(password: str) -> str:
    """Hash password using bcrypt directly"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password - supports both legacy SHA256 and bcrypt hashes"""
    # Legacy SHA256 hashes are exactly 64 lowercase hex characters
    if len(hashed_password) == 64 and all(c in '0123456789abcdef' for c in hashed_password):
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password
    # Bcrypt hashes start with $2b$ or $2a$
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

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
    if not user_doc or not verify_password(data.password, user_doc['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Migrate legacy SHA256 hash to bcrypt on successful login
    if len(user_doc['password_hash']) == 64 and all(c in '0123456789abcdef' for c in user_doc['password_hash']):
        new_hash = hash_password(data.password)
        await db.users.update_one({"id": user_doc['id']}, {"$set": {"password_hash": new_hash}})
    
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
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        subscription_tier=current_user.subscription_tier,
        is_admin=current_user.is_admin,
        has_openai_key=bool(current_user.openai_api_key),
        has_telegram_token=bool(current_user.telegram_bot_token),
        telegram_chat_id=current_user.telegram_chat_id
    )
