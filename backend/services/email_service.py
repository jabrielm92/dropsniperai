"""Email notification service using Resend"""
import os
import resend
from typing import Optional, List
from datetime import datetime

# Initialize Resend
resend.api_key = os.environ.get('RESEND_API_KEY')

FROM_EMAIL = "DropSniper AI <noreply@arisolutionsinc.com>"
SUPPORT_EMAIL = "dropsniperai@arisolutionsinc.com"

async def send_welcome_email(to_email: str, user_name: str) -> dict:
    """Send welcome email to new users"""
    if not resend.api_key:
        return {"success": False, "error": "Resend not configured"}
    
    try:
        params = {
            "from": FROM_EMAIL,
            "to": [to_email],
            "subject": "Welcome to DropSniper AI! 🎯",
            "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0A0A0A; color: #ffffff; padding: 40px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #22c55e; margin: 0;">⚡ DropSniper AI</h1>
                </div>
                
                <h2 style="color: #ffffff;">Welcome aboard, {user_name}! 🎉</h2>
                
                <p style="color: #a1a1aa; line-height: 1.6;">
                    You're now part of an elite group of dropshippers who use AI to find winning products before the competition.
                </p>
                
                <div style="background: #121212; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <h3 style="color: #22c55e; margin-top: 0;">🚀 Quick Start:</h3>
                    <ol style="color: #a1a1aa; line-height: 1.8;">
                        <li>Connect your Telegram for daily alerts</li>
                        <li>Check your first batch of winning products</li>
                        <li>Generate launch kits for products you like</li>
                        <li>Export directly to Shopify or WooCommerce</li>
                    </ol>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://dropsniperai.arisolutionsinc.com/dashboard" 
                       style="background: #22c55e; color: #000000; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                        Go to Dashboard
                    </a>
                </div>
                
                <p style="color: #71717a; font-size: 12px; text-align: center; margin-top: 40px;">
                    Questions? Reply to this email or contact {SUPPORT_EMAIL}
                </p>
            </div>
            """
        }
        
        email = resend.Emails.send(params)
        return {"success": True, "id": email.get("id")}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def send_daily_report_email(to_email: str, user_name: str, report_data: dict) -> dict:
    """Send daily product report via email"""
    if not resend.api_key:
        return {"success": False, "error": "Resend not configured"}
    
    products_html = ""
    for p in report_data.get("top_products", [])[:5]:
        trend_color = "#22c55e" if p.get("trend_direction") == "up" else "#ef4444" if p.get("trend_direction") == "down" else "#a1a1aa"
        trend_arrow = "↑" if p.get("trend_direction") == "up" else "↓" if p.get("trend_direction") == "down" else "→"
        products_html += f"""
        <tr style="border-bottom: 1px solid #262626;">
            <td style="padding: 12px; color: #ffffff;">{p.get('name', 'Unknown')}</td>
            <td style="padding: 12px; color: #22c55e; text-align: center;">{p.get('score', 0)}</td>
            <td style="padding: 12px; color: #a1a1aa; text-align: center;">${p.get('source_cost', 0):.2f}</td>
            <td style="padding: 12px; color: #ffffff; text-align: center;">${p.get('sell_price', 0):.2f}</td>
            <td style="padding: 12px; color: {trend_color}; text-align: center;">{trend_arrow} {p.get('trend_percent', 0)}%</td>
        </tr>
        """
    
    try:
        params = {
            "from": FROM_EMAIL,
            "to": [to_email],
            "subject": f"🎯 Your Daily Winners - {datetime.now().strftime('%b %d')}",
            "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto; background: #0A0A0A; color: #ffffff; padding: 40px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #22c55e; margin: 0;">⚡ Daily Intelligence Report</h1>
                    <p style="color: #71717a; margin-top: 5px;">{datetime.now().strftime('%B %d, %Y')}</p>
                </div>
                
                <p style="color: #a1a1aa;">Hey {user_name},</p>
                <p style="color: #a1a1aa; line-height: 1.6;">
                    Our AI scanned <strong style="color: #ffffff;">{report_data.get('products_scanned', 0):,}</strong> products overnight. 
                    Here are your top opportunities:
                </p>
                
                <div style="background: #121212; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <div style="display: flex; justify-content: space-around; text-align: center;">
                        <div>
                            <div style="color: #22c55e; font-size: 24px; font-weight: bold;">{report_data.get('passed_filters', 0)}</div>
                            <div style="color: #71717a; font-size: 12px;">Passed Filters</div>
                        </div>
                        <div>
                            <div style="color: #22c55e; font-size: 24px; font-weight: bold;">{report_data.get('fully_validated', 0)}</div>
                            <div style="color: #71717a; font-size: 12px;">Validated</div>
                        </div>
                        <div>
                            <div style="color: #22c55e; font-size: 24px; font-weight: bold;">{report_data.get('ready_to_launch', 0)}</div>
                            <div style="color: #71717a; font-size: 12px;">Ready to Launch</div>
                        </div>
                    </div>
                </div>
                
                <h3 style="color: #ffffff; margin-top: 30px;">🏆 Top 5 Winners</h3>
                <table style="width: 100%; border-collapse: collapse; background: #121212; border-radius: 8px;">
                    <thead>
                        <tr style="border-bottom: 1px solid #262626;">
                            <th style="padding: 12px; color: #71717a; text-align: left;">Product</th>
                            <th style="padding: 12px; color: #71717a; text-align: center;">Score</th>
                            <th style="padding: 12px; color: #71717a; text-align: center;">Cost</th>
                            <th style="padding: 12px; color: #71717a; text-align: center;">Sell</th>
                            <th style="padding: 12px; color: #71717a; text-align: center;">Trend</th>
                        </tr>
                    </thead>
                    <tbody>
                        {products_html}
                    </tbody>
                </table>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://dropsniperai.arisolutionsinc.com/dashboard" 
                       style="background: #22c55e; color: #000000; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                        View Full Report
                    </a>
                </div>
                
                <p style="color: #71717a; font-size: 12px; text-align: center; margin-top: 40px;">
                    You're receiving this because you have email alerts enabled.<br/>
                    <a href="https://dropsniperai.arisolutionsinc.com/settings" style="color: #22c55e;">Manage preferences</a>
                </p>
            </div>
            """
        }
        
        email = resend.Emails.send(params)
        return {"success": True, "id": email.get("id")}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def send_competitor_alert_email(to_email: str, user_name: str, alert_data: dict) -> dict:
    """Send competitor activity alert"""
    if not resend.api_key:
        return {"success": False, "error": "Resend not configured"}
    
    try:
        params = {
            "from": FROM_EMAIL,
            "to": [to_email],
            "subject": f"⚠️ Competitor Alert: {alert_data.get('store_name', 'Store')}",
            "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0A0A0A; color: #ffffff; padding: 40px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #f59e0b; margin: 0;">⚠️ Competitor Alert</h1>
                </div>
                
                <p style="color: #a1a1aa;">Hey {user_name},</p>
                
                <div style="background: #121212; border-radius: 8px; padding: 20px; margin: 20px 0; border-left: 4px solid #f59e0b;">
                    <h3 style="color: #ffffff; margin-top: 0;">{alert_data.get('store_name', 'Competitor')}</h3>
                    <p style="color: #a1a1aa; margin-bottom: 0;">
                        {alert_data.get('message', 'New activity detected')}
                    </p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://dropsniperai.arisolutionsinc.com/competitors" 
                       style="background: #f59e0b; color: #000000; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                        View Details
                    </a>
                </div>
                
                <p style="color: #71717a; font-size: 12px; text-align: center;">
                    <a href="https://dropsniperai.arisolutionsinc.com/settings" style="color: #22c55e;">Manage alert preferences</a>
                </p>
            </div>
            """
        }
        
        email = resend.Emails.send(params)
        return {"success": True, "id": email.get("id")}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def send_trial_ending_email(to_email: str, user_name: str, hours_left: int) -> dict:
    """Send trial ending reminder"""
    if not resend.api_key:
        return {"success": False, "error": "Resend not configured"}
    
    try:
        params = {
            "from": FROM_EMAIL,
            "to": [to_email],
            "subject": f"⏰ Your trial ends in {hours_left} hours",
            "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0A0A0A; color: #ffffff; padding: 40px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #22c55e; margin: 0;">⚡ DropSniper AI</h1>
                </div>
                
                <h2 style="color: #ffffff; text-align: center;">Your trial ends in {hours_left} hours ⏰</h2>
                
                <p style="color: #a1a1aa; text-align: center; line-height: 1.6;">
                    Hey {user_name}, don't lose access to your winning product pipeline!
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://dropsniperai.arisolutionsinc.com/pricing" 
                       style="background: #22c55e; color: #000000; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                        Upgrade Now
                    </a>
                </div>
                
                <p style="color: #71717a; font-size: 12px; text-align: center;">
                    Questions? Contact {SUPPORT_EMAIL}
                </p>
            </div>
            """
        }
        
        email = resend.Emails.send(params)
        return {"success": True, "id": email.get("id")}
    except Exception as e:
        return {"success": False, "error": str(e)}
