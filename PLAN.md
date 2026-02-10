# DropSniper AI - Production Readiness Plan

## What's Real vs Mock Today

| Component | Status | Details |
|-----------|--------|---------|
| Tier system & feature gating | REAL | Works correctly |
| Auth (bcrypt + JWT) | REAL | Secure, but JWT_SECRET has unsafe fallback |
| Stripe payments | REAL | Checkout, webhooks, portal all wired |
| AI Scanner (ai_scanner.py) | REAL | Uses GPT-4o via OpenAI API |
| Telegram Bot | REAL | Sends real messages via Telegram API |
| Scheduler (APScheduler) | REAL | Cron jobs run, but report stats are hardcoded |
| Google Trends (routes/trends.py) | REAL | Uses pytrends library |
| Email verification | REAL | Uses Resend API |
| Export (Shopify/WooCommerce CSV) | REAL | Generates proper CSV |
| Product Scanners (scanners.py) | **MOCK** | 100% hardcoded product lists |
| Competitor Spy | **MOCK** | random.sample() from hardcoded list |
| Browser Agent | **OPTIONAL** | Requires browser-use lib, not installed |
| Scheduler report stats | **HARDCODED** | "2847 products scanned" every day |
| Free tier Telegram | **BROKEN** | Only sends 1 report ever |

## Fixes Needed (Ordered by Priority)

### Phase 1: Critical Infrastructure

1. **JWT_SECRET** - Require env var, fail on startup if missing
2. **Hardcoded admin email** - Move to env var

### Phase 2: Make Scanners Real (Sniper + Elite Core)

3. **Replace scanners.py mock data with real scraping/API logic**
   - TikTok: Use TikTok Creative Center API or scrape trending hashtags
   - Amazon: Scrape Movers & Shakers / Best Sellers pages
   - AliExpress: Scrape trending/hot products
   - Google Trends: Already have pytrends - wire it into scanner
   - Meta Ad Library: Use Meta Ad Library API (requires Meta app)

4. **AI Scanner improvements**
   - Use OpenAI JSON mode (`response_format={"type": "json_object"}`)
   - Add validation for returned product data
   - Better error handling (log failures, don't silently swallow)

### Phase 3: Competitor Spy (Elite Feature)

5. **Replace mock competitor_spy.py with real scraping**
   - Scrape Shopify stores (products.json endpoint)
   - Track product additions/removals/price changes over time
   - Calculate estimated revenue from product data
   - Store snapshots in MongoDB for change detection

### Phase 4: Scheduler & Telegram Fixes

6. **Fix hardcoded report stats** - Calculate actual scan counts from DB
7. **Fix free tier Telegram** - Remove `free_report_sent` one-time limit
8. **Ensure daily_products always filtered by user_id**

### Phase 5: Missing Supplier/ROI Features

9. **Real supplier sourcing** - Scrape AliExpress for supplier data per product
10. **ROI calculator** - Use real cost data instead of AI-estimated values

## What I Need From You

- **Meta Ad Library access**: Do you have a Meta developer app for the Ad Library API? Or should I scrape the public ad library?
- **Proxy/scraping service**: Real scraping of TikTok/Amazon/AliExpress will get rate-limited. Do you have a proxy service (ScraperAPI, Bright Data, etc.) or should I build with httpx + user-agent rotation?
- **Browser automation**: The ai_browser_agent.py uses `browser-use` library. Do you want to deploy with a headless browser (Playwright/Puppeteer) on Railway, or keep scraping lightweight with HTTP requests only?
- **AliExpress API**: Do you have an AliExpress affiliate/dropship API key, or should I scrape the site directly?
