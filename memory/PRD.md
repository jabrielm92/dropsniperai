# DropSniper AI - Product Requirements Document

## Overview
DropSniper AI is a full-stack AI-powered dropshipping product research SaaS platform that automates product discovery, validation, competitor monitoring, and launch preparation.

## Tech Stack
- **Frontend**: React 18 + Tailwind CSS + Shadcn UI → Vercel
- **Backend**: FastAPI + Pydantic → Railway  
- **Database**: MongoDB Atlas
- **Payments**: Stripe (24-hour trial)
- **Notifications**: Telegram Bot API
- **Trends**: Google Trends (pytrends)

## Pricing Tiers

| Tier | Price | Status | Features |
|------|-------|--------|----------|
| **Sniper** | $29/mo | Active | 10 products/day, email, basic filters |
| **Elite** | $79/mo | Active | Unlimited, Telegram, competitor spy, exports |
| **Agency** | $149/mo | Coming Soon | Team seats, white-label, API |
| **Enterprise** | Custom | Coming Soon | Custom integrations |

## Implemented Features ✅

### Core
- [x] JWT Authentication
- [x] Dashboard with daily intelligence report
- [x] Product discovery with scoring
- [x] Launch kit generator (ad copy, video scripts)
- [x] Settings with configurable filters

### Intelligence
- [x] Multi-source scanner (TikTok, Amazon, AliExpress)
- [x] Google Trends integration (pytrends)
- [x] Saturation radar
- [x] Competitor spy & alerts

### Integrations
- [x] Telegram bot notifications
- [x] Stripe payments (24-hour trial)
- [x] Shopify CSV export
- [x] WooCommerce CSV export

### Admin & Multi-tenant
- [x] Admin panel (jabriel@arisolutionsinc.com)
- [x] User tier management
- [x] Per-user API key storage
- [x] Tier-based feature gating

### Pages
- [x] Landing page (features, testimonials, Telegram preview)
- [x] Pricing page (2 active + 2 coming soon)
- [x] Terms of Service
- [x] Privacy Policy
- [x] Setup Wizard for new users

## Deployment Ready
- [x] Railway configuration (backend)
- [x] Vercel configuration (frontend)
- [x] MongoDB Atlas compatible
- [x] Environment variables documented
- [x] `/app/DEPLOYMENT_GUIDE.md` - Click-by-click instructions

## Environment Variables

### Railway (Backend)
- `MONGO_URL` - MongoDB connection string
- `DB_NAME` - Database name
- `JWT_SECRET` - Auth secret
- `STRIPE_SECRET_KEY` - Stripe API key
- `STRIPE_PUBLISHABLE_KEY` - Stripe public key
- `STRIPE_WEBHOOK_SECRET` - Webhook verification
- `FRONTEND_URL` - Vercel app URL

### Vercel (Frontend)
- `REACT_APP_BACKEND_URL` - Railway backend URL

## Admin Access
Email: `jabriel@arisolutionsinc.com` → Auto-admin on register

## Backlog
- [ ] Background job scheduling (daily scans)
- [ ] Email notifications
- [ ] Team seats (Agency tier)
- [ ] White-label reports
- [ ] API rate limiting
