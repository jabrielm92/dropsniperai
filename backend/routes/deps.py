"""Database and shared dependencies for routes"""
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import jwt
from datetime import datetime, timezone
from models import User

# MongoDB connection - initialized from main app
db = None
JWT_SECRET = None
JWT_ALGORITHM = "HS256"

security = HTTPBearer()

def init_db(database, secret):
    """Initialize database connection"""
    global db, JWT_SECRET
    db = database
    JWT_SECRET = secret

def get_db():
    """Get database instance"""
    return db

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Verify JWT and return current user"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user_doc:
            raise HTTPException(status_code=401, detail="User not found")
        return User(**user_doc)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Dependency to require admin access"""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
