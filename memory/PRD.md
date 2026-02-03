# DropSniper AI - Product Requirements Document

## Overview
AI-powered dropshipping product research SaaS platform.

**Domain:** dropsniperai.arisolutionsinc.com  
**Support:** dropsniperai@arisolutionsinc.com

## Tech Stack
- **Frontend**: React 18 + Tailwind + Shadcn UI → Vercel
- **Backend**: FastAPI + Pydantic → Railway
- **Database**: MongoDB Atlas
- **Payments**: Stripe (24-hour trial)
- **Email**: Resend (transactional emails)
- **Notifications**: Telegram Bot API (user-provided)

## Pricing Tiers
| Tier | Price | Status |
|------|-------|--------|
| Sniper | $29/mo | Active |
| Elite | $79/mo | Active |
| Agency | $149/mo | Coming Soon |
| Enterprise | Custom | Coming Soon |

## Environment Variables

### Railway (Backend)
| Variable | Required | Description |
|----------|----------|-------------|
| `MONGO_URL` | ✅ | MongoDB Atlas connection string |
| `DB_NAME` | ✅ | Database name (`dropsniper`) |
| `JWT_SECRET` | ✅ | 64-char random string |
| `STRIPE_SECRET_KEY` | ✅ | Stripe secret key |
| `STRIPE_PUBLISHABLE_KEY` | ✅ | Stripe public key |
| `STRIPE_WEBHOOK_SECRET` | ✅ | Stripe webhook secret |
| `RESEND_API_KEY` | ✅ | Resend API key for emails |
| `FRONTEND_URL` | ✅ | `https://dropsniperai.arisolutionsinc.com` |

### Vercel (Frontend)
| Variable | Required | Description |
|----------|----------|-------------|
| `REACT_APP_BACKEND_URL` | ✅ | Railway backend URL |

### User-Provided (via Settings page)
- OpenAI API Key - For AI browser features
- Telegram Bot Token - For personal alerts
- Telegram Chat ID - For receiving messages

## Admin Access
Email: `jabriel@arisolutionsinc.com` → Auto-admin on register

## Implemented Features
- [x] JWT Authentication
- [x] User Registration with Email Verification Flow
- [x] Dashboard + Daily Reports
- [x] Product Discovery + Scoring
- [x] Launch Kit Generator
- [x] Google Trends Integration (Elite+)
- [x] Competitor Spy + Alerts (Elite+)
- [x] Saturation Radar (Elite+)
- [x] Shopify/WooCommerce Export (Elite+)
- [x] Stripe Payments (24hr trial)
- [x] Resend Email Notifications
- [x] Telegram Bot Integration
- [x] Admin Panel
- [x] **Tier-based Feature Gating (enforced on backend)**
- [x] Terms of Service + Privacy Policy

## Tier Feature Gating
| Feature | Required Tier |
|---------|---------------|
| Basic Products | Free |
| Daily Report | Free |
| Launch Kit | Sniper |
| Telegram Alerts | Elite |
| Competitor Spy | Elite |
| Saturation Radar | Elite |
| Export Shopify | Elite |
| Export WooCommerce | Elite |
| Google Trends | Elite |
| Unlimited Products | Elite |
| API Access | Agency |
| Team Seats | Agency |
| White Label | Agency |

## API Endpoint: GET /api/user/tier-status
Returns user's current tier, limits, and feature access.

## Deployment
See `/app/DEPLOYMENT_GUIDE.md` for click-by-click instructions.

## Last Updated
2026-02-03 - P0 & P1 completed
