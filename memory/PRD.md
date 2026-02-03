# ProductScout AI - Product Requirements Document

## Overview
ProductScout AI is a full-stack AI-powered dropshipping product research SaaS platform that automates the entire pipeline from trend discovery to launch preparation. 

**Architecture follows the original ClawdBot concept from X:**
- AI agent controls a real browser (like a human)
- Browses TikTok, Amazon, AliExpress, Google Trends autonomously
- Sends results via Telegram
- Runs on schedule (daily at 7AM style)

## Architecture
- **Frontend**: React + Tailwind + Shadcn UI (Vercel-ready)
- **Backend**: FastAPI + MongoDB (Railway-ready)
- **AI Browser**: browser-use + GPT-4 (autonomous browsing)
- **Notifications**: Telegram Bot API
- **Database**: MongoDB Atlas

## User Personas
1. **Beginner Dropshippers** - Need guidance on what products to sell
2. **Experienced Sellers** - Want to automate research and find winners faster
3. **Agency Owners** - Manage multiple stores, need team collaboration
4. **Side Hustlers** - Limited time, need efficient product discovery

## Core Requirements (Static)
- AI-powered product discovery from multiple sources
- Automated filtering based on customizable criteria
- Profit margin calculations with all fees included
- Launch kit generation with ad copy and targeting
- Daily intelligence reports
- Competitor monitoring
- Multi-channel notifications (Email, Telegram, In-app)

## What's Been Implemented

### Phase 1 - MVP Core (Completed: Feb 3, 2026)
- [x] User authentication (JWT-based)
- [x] Dashboard with daily intelligence report
- [x] Product cards with scores, trends, margins
- [x] Product detail page with sourcing, validation, profit breakdown
- [x] Launch kit generator (ad copy, video scripts, targeting, checklist)
- [x] Settings page with configurable filters
- [x] Pricing page with 4 subscription tiers

### Phase 2 - Intelligence Layer (Completed: Feb 3, 2026)
- [x] Scanner service with multiple data sources:
  - TikTok trending (10M+ views hashtags)
  - Amazon Movers & Shakers
  - AliExpress trending products
  - Google Trends rising searches
  - Meta Ad Library scanner
- [x] Product analysis engine
- [x] Saturation Radar with niche breakdown
- [x] Competition scoring system

### Phase 3 - Competitor Spy (Completed: Feb 3, 2026)
- [x] Add competitor stores to monitor
- [x] Store product tracking
- [x] New product detection
- [x] Alert system for changes
- [x] Competitor product details view

## Prioritized Backlog

### P0 - Critical for Launch
- [ ] OpenAI integration for AI-enhanced ad copy generation
- [ ] Telegram Bot API integration for daily alerts
- [ ] Stripe subscription integration for payments
- [ ] Real web scraping implementation (replace mock data)

### P1 - High Priority
- [ ] Email notifications (SendGrid/Resend integration)
- [ ] Background job scheduling (cron for daily scans)
- [ ] User onboarding flow
- [ ] Product boards/collections feature

### P2 - Medium Priority
- [ ] Advanced analytics dashboard
- [ ] Export reports to PDF
- [ ] Team collaboration features
- [ ] API access for power users
- [ ] Seasonal trend calendar

### P3 - Nice to Have
- [ ] Chrome extension for quick product analysis
- [ ] Direct Shopify/WooCommerce import
- [ ] Price tracking history
- [ ] AI chat assistant for product questions

## Next Tasks List
1. Integrate OpenAI API for enhanced ad copy generation
2. Set up Telegram Bot for push notifications
3. Implement Stripe subscriptions
4. Deploy: Frontend to Vercel, Backend to Railway
5. Replace mock scanner data with real scraping logic
6. Add email notification service

## Technical Decisions
- Using simulated/mock data for scanners (structured for easy replacement with real scraping)
- JWT authentication with 24-hour token expiration
- MongoDB for flexible document storage
- Shadcn UI for consistent component library
- Dark theme optimized for long working sessions

## Data Sources (Simulated - Ready for Real Integration)
| Source | Data Type | Implementation Status |
|--------|-----------|----------------------|
| TikTok | Trending hashtags, viral products | Mock (ready for scraping) |
| Amazon | Movers & Shakers | Mock (ready for API/scraping) |
| AliExpress | Trending, pricing | Mock (ready for scraping) |
| Google Trends | Rising searches | Mock (ready for API) |
| Meta Ad Library | Competition analysis | Mock (ready for API) |

## Deployment Configuration
- Frontend: Vercel (process.env.REACT_APP_BACKEND_URL)
- Backend: Railway (port 8001, /api prefix)
- Database: MongoDB Atlas (MONGO_URL env var)
