"""
AI Product Scanner - Uses OpenAI to analyze and discover trending products.
Combines real web scraping data with AI analysis for enrichment and scoring.

Key improvements:
- Multiple image source fallbacks (AliExpress, Amazon CDN, product search)
- AI enrichment only uses scraped data, never generates fake products
- Better validation and field population for product detail page
- Supplier data enrichment with real AliExpress data
"""
import asyncio
import json
import logging
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from openai import AsyncOpenAI
import httpx

logger = logging.getLogger(__name__)

# Headers for image fetching
_IMAGE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "sec-ch-ua": '"Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}


async def _fetch_product_image(product_name: str) -> str:
    """Search multiple sources for a real product image URL.

    Strategy:
    1. AliExpress search (script JSON + img tags)
    2. Amazon search page (img tags)
    """
    try:
        async with httpx.AsyncClient(timeout=12, follow_redirects=True) as client:
            # Strategy 1: AliExpress search
            url = f"https://www.aliexpress.com/w/wholesale-{quote_plus(product_name)}.html"
            try:
                resp = await client.get(url, headers=_IMAGE_HEADERS)
                if resp.status_code == 200:
                    text = resp.text
                    # Extract from script JSON data
                    img_matches = re.findall(
                        r'"imgUrl"\s*:\s*"((?:https?:)?//[^"]+\.(?:jpg|jpeg|png|webp)[^"]*)"',
                        text
                    )
                    for img in img_matches[:3]:
                        if img.startswith("//"):
                            img = "https:" + img
                        if "alicdn.com" in img or "ae01." in img:
                            return img

                    # Fallback: parse img tags
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(text, "html.parser")
                    for img_tag in soup.select("img[src*='alicdn.com'], img[src*='ae01.alicdn'], img[data-src*='alicdn']"):
                        src = img_tag.get("src", img_tag.get("data-src", ""))
                        if src and ("jpg" in src or "png" in src or "webp" in src):
                            if src.startswith("//"):
                                src = "https:" + src
                            return src
            except Exception as e:
                logger.debug(f"AliExpress image fetch failed for '{product_name}': {e}")

            # Strategy 2: Try Amazon search
            try:
                amazon_url = f"https://www.amazon.com/s?k={quote_plus(product_name)}"
                resp = await client.get(amazon_url, headers={
                    **_IMAGE_HEADERS,
                    "Accept": "text/html,application/xhtml+xml",
                })
                if resp.status_code == 200:
                    # Look for product images in the search results
                    img_matches = re.findall(
                        r'"(https://m\.media-amazon\.com/images/I/[^"]+\.(?:jpg|png|webp))"',
                        resp.text
                    )
                    for img in img_matches[:3]:
                        if "_AC_" in img or "_SL" in img or "_SX" in img:
                            return img
            except Exception as e:
                logger.debug(f"Amazon image fetch failed for '{product_name}': {e}")

    except Exception as e:
        logger.debug(f"Image fetch failed for '{product_name}': {e}")
    return ""


async def _enrich_images(products: List[Dict]) -> List[Dict]:
    """Fetch real images for products that don't have valid image URLs."""
    async def _enrich_one(p):
        img = p.get("image_url", "")
        # Check if image is missing, a google redirect, or too short to be a real URL
        if not img or "google.com/search" in img or len(img) < 10 or img.startswith("data:"):
            real_img = await _fetch_product_image(p.get("name", ""))
            if real_img:
                p["image_url"] = real_img
        # Fix protocol-relative URLs
        elif img.startswith("//"):
            p["image_url"] = "https:" + img
        return p

    # Fetch images concurrently (max 5 at a time)
    semaphore = asyncio.Semaphore(5)
    async def _limited(p):
        async with semaphore:
            return await _enrich_one(p)

    results = await asyncio.gather(*[_limited(p) for p in products], return_exceptions=True)
    return [r for r in results if isinstance(r, dict)]


class AIProductScanner:
    """
    AI-powered product scanner that:
    1. Runs real web scrapers to gather raw product data
    2. Uses GPT-4o to enrich, score, and analyze the results
    3. Never generates fake products - only enriches real scraped data
    """

    def __init__(self, openai_key: str):
        self.client = AsyncOpenAI(api_key=openai_key)
        self.model = "gpt-4o"

    async def _call_openai_json(self, system_prompt: str, user_prompt: str) -> Dict:
        """Make OpenAI API call with JSON mode for reliable parsing"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=4000,
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"OpenAI returned invalid JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise

    async def scan_trending_products(self, filters: Dict = None) -> Dict[str, Any]:
        """
        1. Scrape real data from Amazon, AliExpress, TikTok, Google Trends
        2. Send scraped data to GPT-4o for enrichment and scoring
        3. If no scraped data at all, return empty rather than generating fake products
        """
        # Step 1: Run real scrapers
        from services.scanners import ProductScoutEngine
        scout = ProductScoutEngine()

        try:
            raw_results = await scout.run_full_scan()
            raw_products = raw_results.get("products", [])
            source_stats = raw_results.get("source_stats", {})
        except Exception as e:
            logger.warning(f"Real scrapers failed: {e}")
            raw_products = []
            source_stats = {}

        # Step 2: Enrich with AI (only if we have real data)
        filter_instructions = self._build_filter_instructions(filters)

        if raw_products:
            # We have real data - ask AI to enrich and score it
            products_summary = json.dumps(raw_products[:25], default=str)
            system_prompt = """You are a dropshipping product research expert. You will receive REAL scraped product data from multiple sources (TikTok, Amazon, AliExpress, Google Trends).

Your job is to ANALYZE, ENRICH, and SCORE these REAL products for dropshipping potential.

CRITICAL RULES:
- You MUST only work with the products provided in the scraped data
- Do NOT invent or add products that are not in the scraped data
- Use the real data (prices, order counts, views, rank changes) to inform your scoring
- Keep the original image_url from scraped data if present
- Keep the original source from scraped data

You MUST respond with a JSON object containing a "products" array."""

            user_prompt = f"""Here is REAL product data scraped just now from TikTok, Amazon, AliExpress, and Google Trends:

{products_summary}

For EACH product in the scraped data above, provide enriched data:
- name: Clean product name (from the scraped data, don't invent new ones)
- source: Original source from scraped data (tiktok/amazon/aliexpress/google_trends)
- image_url: Keep the original image_url from the scraped data if available, otherwise leave empty string
- estimated_views: Estimated viral reach (use trend_data views/video_count if available, otherwise estimate based on the product category)
- source_cost: Supplier cost estimate in USD. If trend_data.price is available, use that. Otherwise estimate based on the product type.
- recommended_price: Recommended selling price (2.5-4x source cost for good margins)
- margin_percent: Profit margin percentage (number)
- trend_score: How strong the trend is 1-100 (use trend_data.growth_rate, rank_change, or order velocity to inform this)
- overall_score: Overall dropshipping opportunity 1-100 (composite of trend, margin, competition)
- category: Product category (Electronics, Beauty, Home & Kitchen, Fashion, Health, etc.)
- why_trending: Brief 1-sentence reason why it's trending (be specific, reference the source)
- saturation_level: low/medium/high based on competition signals
- active_fb_ads: Estimated number of Facebook ads for this product type (number, be realistic)
- trend_direction: up/down/stable (use trend_data if available)
- competition_score: Competition favorability 1-100 (higher = less competition = better)
- profit_score: Profit potential 1-100
- search_volume: Estimated monthly search volume (number)
{filter_instructions}

Return as JSON: {{"products": [...]}}"""
        else:
            # No scraper data at all - return empty result
            logger.warning("All scrapers returned 0 products. Cannot enrich without real data.")
            return {
                "success": True,
                "products": [],
                "count": 0,
                "source_stats": source_stats,
                "raw_products_scraped": 0,
                "message": "Scrapers could not reach external sources. Try again later or check your network connection.",
                "scanned_at": datetime.now(timezone.utc).isoformat(),
            }

        try:
            result = await self._call_openai_json(system_prompt, user_prompt)
            products = result.get("products", [])

            # Validate and clean each product
            validated = []
            for p in products:
                cleaned = self._validate_product(p)
                if cleaned:
                    cleaned["discovered_at"] = datetime.now(timezone.utc).isoformat()
                    cleaned["ai_enriched"] = True
                    validated.append(cleaned)

            # Fetch real images from AliExpress for products missing images
            validated = await _enrich_images(validated)

            return {
                "success": True,
                "products": validated,
                "count": len(validated),
                "source_stats": source_stats,
                "raw_products_scraped": len(raw_products),
                "scanned_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"AI enrichment failed: {e}")
            # Return raw scraped data without AI enrichment - still real data
            if raw_products:
                # Add basic fields so products are usable
                basic_products = []
                for p in raw_products[:10]:
                    basic = self._make_basic_product(p)
                    basic_products.append(basic)
                return {
                    "success": True,
                    "products": basic_products,
                    "count": len(basic_products),
                    "source_stats": source_stats,
                    "ai_enrichment_failed": True,
                    "scanned_at": datetime.now(timezone.utc).isoformat(),
                }
            return {"success": False, "error": str(e), "products": [], "count": 0}

    async def scan_source(self, source: str, filters: Dict = None) -> Dict[str, Any]:
        """Scan a specific source with real scraping + AI enrichment"""
        from services.scanners import (
            TikTokScanner, AmazonScanner, AliExpressScanner, GoogleTrendsScanner
        )

        # Run real scraper for this source
        raw_products = []
        try:
            scanners = {
                "tiktok": TikTokScanner().scan_trending,
                "amazon": AmazonScanner().scan_movers_shakers,
                "aliexpress": AliExpressScanner().scan_trending,
                "google_trends": GoogleTrendsScanner().scan_rising_terms,
            }
            scanner_fn = scanners.get(source)
            if scanner_fn:
                raw_products = await scanner_fn()
        except Exception as e:
            logger.warning(f"Real scraper failed for {source}: {e}")

        source_prompts = {
            "tiktok": "Focus on products going viral on TikTok with #tiktokmademebuyit. These should have high view counts and engagement.",
            "amazon": "Focus on Amazon Movers & Shakers - items with biggest rank increases in the past 24 hours.",
            "aliexpress": "Focus on hot-selling AliExpress products with high order counts and good dropshipping margins.",
            "google_trends": "Focus on rising search terms related to physical products with breakout growth.",
        }

        filter_instructions = self._build_filter_instructions(filters)

        if raw_products:
            products_summary = json.dumps(raw_products[:15], default=str)
            system_prompt = f"""You are a dropshipping expert specializing in {source} trends.
Analyze the REAL scraped data below and enrich it with scores and recommendations.
CRITICAL: Only work with products from the scraped data. Do NOT invent new products.
You MUST respond with a JSON object containing a "products" array."""

            user_prompt = f"""Real scraped data from {source}:

{products_summary}

Enrich EACH product from the data above with:
- name: Clean product name (from scraped data)
- source: "{source}"
- image_url: Keep from scraped data if available, otherwise empty string
- estimated_views (number), source_cost (number in USD), recommended_price (number in USD)
- margin_percent (number), trend_score (1-100), overall_score (1-100), category
- why_trending (specific reason), saturation_level (low/medium/high), trend_direction (up/down/stable)
- active_fb_ads (number), competition_score (1-100), profit_score (1-100), search_volume (number)
{filter_instructions}

Return as JSON: {{"products": [...]}}"""
        else:
            # No scraped data for this source - return empty
            logger.warning(f"Scraper returned 0 products for {source}.")
            return {
                "success": True,
                "source": source,
                "products": [],
                "count": 0,
                "raw_scraped": 0,
                "message": f"Could not scrape {source}. The site may be blocking requests. Try again later.",
                "scanned_at": datetime.now(timezone.utc).isoformat(),
            }

        try:
            result = await self._call_openai_json(system_prompt, user_prompt)
            products = [self._validate_product(p) for p in result.get("products", []) if self._validate_product(p)]

            for p in products:
                p["discovered_at"] = datetime.now(timezone.utc).isoformat()
                p["ai_enriched"] = True

            # Fetch real images for products missing them
            products = await _enrich_images(products)

            return {
                "success": True,
                "source": source,
                "products": products,
                "count": len(products),
                "raw_scraped": len(raw_products),
                "scanned_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            if raw_products:
                basic_products = [self._make_basic_product(p) for p in raw_products[:8]]
                return {
                    "success": True,
                    "source": source,
                    "products": basic_products,
                    "count": len(basic_products),
                    "ai_enrichment_failed": True,
                    "scanned_at": datetime.now(timezone.utc).isoformat(),
                }
            return {"success": False, "source": source, "error": str(e), "products": [], "count": 0}

    async def analyze_product(self, product_name: str) -> Dict[str, Any]:
        """Deep analysis of a specific product with real competition data"""
        from services.scanners import MetaAdLibraryScanner, AliExpressScanner

        ad_data = {}
        suppliers = []
        try:
            meta = MetaAdLibraryScanner()
            ad_data = await meta.scan_product_ads(product_name)
        except Exception as e:
            logger.warning(f"Meta Ad scrape failed for analysis: {e}")

        try:
            ali = AliExpressScanner()
            suppliers = await ali.find_suppliers(product_name)
        except Exception as e:
            logger.warning(f"AliExpress supplier search failed for analysis: {e}")

        # Build context for AI analysis
        context = f"Real competition data: {json.dumps(ad_data, default=str)}\n"
        if suppliers:
            context += f"Real supplier data: {json.dumps(suppliers[:5], default=str)}\n"

        system_prompt = """You are a dropshipping competition analyst. You will receive real scraped data about a product's competition and suppliers.
Analyze for market viability. You MUST respond with a valid JSON object."""

        user_prompt = f"""Analyze "{product_name}" for dropshipping potential.

{context}

Provide a JSON object with:
- competition_level: low/medium/high
- estimated_fb_ads: Number of Facebook ads (use real data if available: {ad_data.get('total_ads', 'unknown')})
- saturation_score: 1-100 (100 = very saturated)
- recommendation: "launch" / "caution" / "avoid"
- supplier_estimate: Best supplier cost (use real data if available)
- recommended_price: Suggested selling price
- target_audience: Who to target
- ad_angles: 3 potential ad angles/hooks
- risks: Potential risks
- opportunity_score: 1-100 overall opportunity
- suppliers: Top supplier options with pricing

Return as JSON object."""

        try:
            analysis = await self._call_openai_json(system_prompt, user_prompt)
            if suppliers:
                analysis["real_suppliers"] = suppliers[:5]
            if ad_data.get("total_ads"):
                analysis["real_ad_count"] = ad_data["total_ads"]
                analysis["real_advertisers"] = ad_data.get("top_advertisers", [])

            return {
                "success": True,
                "product_name": product_name,
                "analysis": analysis,
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            return {"success": False, "product_name": product_name, "error": str(e)}

    async def run_full_scan(self, filters: Dict = None) -> Dict[str, Any]:
        """Run full scan: real scraping across all sources + AI enrichment"""
        return await self.scan_trending_products(filters)

    def _build_filter_instructions(self, filters: Dict = None) -> str:
        """Build filter instructions for AI prompts"""
        if not filters:
            return ""
        instructions = "\nFilter requirements:"
        if filters.get("min_sell_price") or filters.get("min_price"):
            price = filters.get("min_sell_price") or filters.get("min_price")
            instructions += f"\n- Only products with recommended price above ${price}"
        if filters.get("max_source_cost") or filters.get("max_price"):
            cost = filters.get("max_source_cost") or filters.get("max_price")
            instructions += f"\n- Only products with source cost below ${cost}"
        if filters.get("categories"):
            instructions += f"\n- Focus on: {', '.join(filters['categories'])}"
        if filters.get("min_margin_percent"):
            instructions += f"\n- Minimum margin: {filters['min_margin_percent']}%"
        if filters.get("max_fb_ads"):
            instructions += f"\n- Max Facebook ads: {filters['max_fb_ads']}"
        return instructions

    def _validate_product(self, product: Dict) -> Optional[Dict]:
        """Validate and clean a product dict, ensuring all fields needed for product detail page"""
        if not product or not product.get("name"):
            return None

        try:
            name = str(product.get("name", "Unknown"))[:100]
            image_url = product.get("image_url", "")
            if isinstance(image_url, str) and image_url.startswith("//"):
                image_url = "https:" + image_url

            source_cost = float(product.get("source_cost", 0) or 0)
            recommended_price = float(product.get("recommended_price", 0) or 0)
            margin_percent = float(product.get("margin_percent", 0) or 0)

            # Auto-calculate margin if not provided
            if not margin_percent and source_cost > 0 and recommended_price > source_cost:
                margin_percent = round((recommended_price - source_cost) / recommended_price * 100, 1)

            overall_score = max(0, min(100, int(product.get("overall_score", 50) or 50)))
            trend_score = max(0, min(100, int(product.get("trend_score", 50) or 50)))

            return {
                "name": name,
                "image_url": image_url,
                "source": str(product.get("source", "unknown")),
                "estimated_views": int(product.get("estimated_views", 0) or 0),
                "source_cost": source_cost,
                "recommended_price": recommended_price,
                "margin_percent": margin_percent,
                "trend_score": trend_score,
                "overall_score": overall_score,
                "competition_score": max(0, min(100, int(product.get("competition_score", overall_score) or overall_score))),
                "profit_score": max(0, min(100, int(product.get("profit_score", overall_score) or overall_score))),
                "category": str(product.get("category", "General"))[:50],
                "why_trending": str(product.get("why_trending", ""))[:200],
                "saturation_level": str(product.get("saturation_level", "medium")),
                "active_fb_ads": int(product.get("active_fb_ads", 0) or 0),
                "trend_direction": str(product.get("trend_direction", "stable")),
                "trend_percent": float(product.get("trend_percent", 0) or 0),
                "search_volume": int(product.get("search_volume", 0) or 0),
                "shopify_stores": int(product.get("shopify_stores", 0) or 0),
                "source_platforms": product.get("source_platforms", [str(product.get("source", "unknown"))]),
                "trend_data": product.get("trend_data", {}),
            }
        except (ValueError, TypeError) as e:
            logger.warning(f"Product validation failed: {e} - {product.get('name', 'unknown')}")
            return None

    def _make_basic_product(self, raw: Dict) -> Dict:
        """Create a basic product from raw scraped data without AI enrichment.
        Ensures all required fields are present for the product detail page."""
        name = str(raw.get("name", "Unknown"))[:100]
        source = str(raw.get("source", "unknown"))
        image_url = raw.get("image_url", "")
        if isinstance(image_url, str) and image_url.startswith("//"):
            image_url = "https:" + image_url
        trend_data = raw.get("trend_data", {})

        # Extract price from trend_data
        price = float(trend_data.get("price", trend_data.get("current_price", 0)) or 0)
        # For Amazon products, the current_price is the retail price, source cost would be lower
        source_cost = price * 0.3 if source == "amazon" and price > 0 else price
        recommended_price = price if source == "amazon" else price * 3 if price > 0 else 0

        orders = int(trend_data.get("orders_30d", 0) or 0)
        growth = int(trend_data.get("growth_percent", trend_data.get("growth_rate", 0)) or 0)

        # Score based on available data
        if orders > 1000:
            overall_score = min(95, 70 + (orders // 500))
        elif growth > 100:
            overall_score = min(90, 60 + (growth // 50))
        else:
            overall_score = 50

        return {
            "name": name,
            "image_url": image_url,
            "source": source,
            "estimated_views": int(trend_data.get("views", trend_data.get("video_count", 0)) or 0),
            "source_cost": round(source_cost, 2),
            "recommended_price": round(recommended_price, 2),
            "margin_percent": round((recommended_price - source_cost) / recommended_price * 100, 1) if recommended_price > source_cost else 0,
            "trend_score": min(100, max(20, overall_score)),
            "overall_score": overall_score,
            "competition_score": 50,
            "profit_score": 50,
            "category": str(trend_data.get("category", "General")),
            "why_trending": f"Trending on {source}",
            "saturation_level": "medium",
            "active_fb_ads": 0,
            "trend_direction": str(trend_data.get("trend_direction", "up" if growth > 0 else "stable")),
            "trend_percent": float(growth),
            "search_volume": 0,
            "shopify_stores": 0,
            "source_platforms": [source],
            "trend_data": trend_data,
            "discovered_at": datetime.now(timezone.utc).isoformat(),
            "ai_enriched": False,
        }


def create_scanner(openai_key: str) -> AIProductScanner:
    """Factory function to create scanner with user's key"""
    return AIProductScanner(openai_key)
