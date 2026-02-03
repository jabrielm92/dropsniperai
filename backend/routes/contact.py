"""Contact form route"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import resend

router = APIRouter(prefix="/contact", tags=["contact"])

resend.api_key = os.environ.get('RESEND_API_KEY')
SUPPORT_EMAIL = "dropsniperai@arisolutionsinc.com"

class ContactForm(BaseModel):
    name: str
    email: str
    subject: str = ""
    message: str

@router.post("")
async def send_contact_message(form: ContactForm):
    """Send contact form message via Resend"""
    if not resend.api_key:
        raise HTTPException(status_code=500, detail="Email service not configured")
    
    try:
        # Send to support
        resend.Emails.send({
            "from": "DropSniper AI <noreply@arisolutionsinc.com>",
            "to": [SUPPORT_EMAIL],
            "subject": f"Contact Form: {form.subject or 'New Message'} - from {form.name}",
            "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; padding: 20px;">
                <h2>New Contact Form Submission</h2>
                <p><strong>From:</strong> {form.name}</p>
                <p><strong>Email:</strong> {form.email}</p>
                <p><strong>Subject:</strong> {form.subject or 'N/A'}</p>
                <hr style="border: 1px solid #eee; margin: 20px 0;">
                <p><strong>Message:</strong></p>
                <p style="white-space: pre-wrap;">{form.message}</p>
            </div>
            """
        })
        
        # Send confirmation to user
        resend.Emails.send({
            "from": "DropSniper AI <noreply@arisolutionsinc.com>",
            "to": [form.email],
            "subject": "We received your message - DropSniper AI",
            "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; padding: 20px; background: #0A0A0A; color: #fff;">
                <h2 style="color: #22c55e;">Thanks for reaching out, {form.name}!</h2>
                <p style="color: #a1a1aa;">We've received your message and will get back to you within 24 hours.</p>
                <hr style="border: 1px solid #333; margin: 20px 0;">
                <p style="color: #71717a; font-size: 12px;">This is an automated confirmation. Please don't reply to this email.</p>
                <p style="color: #71717a; font-size: 12px;">- The DropSniper AI Team</p>
            </div>
            """
        })
        
        return {"success": True, "message": "Message sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
