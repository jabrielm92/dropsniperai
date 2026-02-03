"""Email verification routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
import os
import resend
import secrets

from routes.deps import get_db

router = APIRouter(prefix="/verify", tags=["verification"])

resend.api_key = os.environ.get('RESEND_API_KEY')

class SendVerificationRequest(BaseModel):
    email: str
    name: str

class VerifyCodeRequest(BaseModel):
    email: str
    code: str

def generate_code():
    """Generate 6-digit verification code"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(6)])

@router.post("/send")
async def send_verification_code(request: SendVerificationRequest):
    """Send verification code to email"""
    if not resend.api_key:
        raise HTTPException(status_code=500, detail="Email service not configured")
    
    db = get_db()
    
    # Check if email already registered
    existing = await db.users.find_one({"email": request.email})
    if existing and existing.get("email_verified"):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate code
    code = generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    # Store verification code
    await db.verification_codes.update_one(
        {"email": request.email},
        {
            "$set": {
                "code": code,
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        },
        upsert=True
    )
    
    # Send email
    try:
        resend.Emails.send({
            "from": "DropSniper AI <noreply@arisolutionsinc.com>",
            "to": [request.email],
            "subject": "Your verification code - DropSniper AI",
            "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0A0A0A; color: #ffffff; padding: 40px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #22c55e; margin: 0;">⚡ DropSniper AI</h1>
                </div>
                
                <h2 style="color: #ffffff; text-align: center;">Verify your email</h2>
                
                <p style="color: #a1a1aa; text-align: center;">
                    Hey {request.name}, enter this code to complete your registration:
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <div style="display: inline-block; background: #121212; border: 2px solid #22c55e; border-radius: 12px; padding: 20px 40px;">
                        <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #22c55e;">{code}</span>
                    </div>
                </div>
                
                <p style="color: #71717a; text-align: center; font-size: 14px;">
                    This code expires in 10 minutes.
                </p>
                
                <p style="color: #71717a; text-align: center; font-size: 12px; margin-top: 30px;">
                    If you didn't request this, you can ignore this email.
                </p>
            </div>
            """
        })
        
        return {"success": True, "message": "Verification code sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check")
async def verify_code(request: VerifyCodeRequest):
    """Verify the code and mark email as verified"""
    db = get_db()
    
    # Find verification code
    record = await db.verification_codes.find_one({"email": request.email})
    
    if not record:
        raise HTTPException(status_code=400, detail="No verification code found. Please request a new one.")
    
    # Check expiry
    expires_at = datetime.fromisoformat(record["expires_at"].replace('Z', '+00:00'))
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=400, detail="Code expired. Please request a new one.")
    
    # Check code
    if record["code"] != request.code:
        raise HTTPException(status_code=400, detail="Invalid code")
    
    # Mark as verified in pending_users or update existing
    await db.pending_verifications.update_one(
        {"email": request.email},
        {"$set": {"verified": True, "verified_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    
    # Clean up verification code
    await db.verification_codes.delete_one({"email": request.email})
    
    return {"success": True, "message": "Email verified"}

@router.post("/resend")
async def resend_code(request: SendVerificationRequest):
    """Resend verification code"""
    return await send_verification_code(request)
