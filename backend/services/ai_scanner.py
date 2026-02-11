"""
AI Product Scanner - Uses OpenAI to analyze and discover trending products.
Combines real web scraping data with AI analysis for enrichment and scoring.
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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


async def _fetch_product_image(product_name: str) -> str:
    """Search AliExpress for a product and return a real image URL."""
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            url = f"https://www.aliexpress.com/w/wholesale-{quote_plus(product_name)}.html"
            resp = await client.get(url, headers=_IMAGE_HEADERS)
            if resp.status_code == 200:
                text = resp.text
                # Extract image URLs from script data
                img_matches = re.findall(r'"imgUrl"\s*:\s*"(https?://[^"]+\.(?:jpg|png|webp)[^"]*)"', text)
                if img_matches:
                    return img_matches[0]
                # Fallback: extract from img tags
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(text, "html.parser")
                for img in soup.select("img[src*='alicdn.com'], img[src*='ae01.alicdn']"):
                    src = img.get("src", "")
                    if src and ("jpg" in src or "png" in src or "webp" in src):
                        if src.startswith("//"):
                            src = "https:" + src
                        return src
    except Exception as e:
        logger.debug(f"Image fetch failed for '{product_name}': {e}")
    return ""


async def _enrich_images(products: List[Dict]) -> List[Dict]:
    """Fetch real images for products that don't have valid image URLs."""
    async def _enrich_one(p):
        img = p.get("image_url", "")
        if not img or "google.com/search" in img or len(img) < 10:
            real_img = await _fetch_product_image(p.get("name", ""))
            if real_img:
                p["image_url"] = real_img
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
                max_tokens=3000,
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
        """
        # Step 1: Run real scrapers
        from services.scanners import ProductScoutEngine
        scout = ProductScoutEngine()

        try:
            raw_results = await scout.run_full_scan()
            raw_products = raw_results.get("products", [])
            source_stats = raw_results.get("source_stats", {})
        except Exception as e:
            logger.warning(f"Real scrapers failed, falling back to AI-only: {e}")
            raw_products = []
            source_stats = {}

        # Step 2: Enrich with AI
        filter_instructions = self._build_filter_instructions(filters)

        if raw_products:
            # We have real data - ask AI to enrich and score it
            products_summary = json.dumps(raw_products[:20], default=str)
            system_prompt = """You are a dropshipping product research expert. You will receive real scraped product data from multiple sources.
Your job is to analyze, enrich, and score these products for dropshipping potential.
You MUST respond with a JSON object containing a "products" array."""

            user_prompt = f"""Here is real product data scraped from TikTok, Amazon, AliExpress, and Google Trends:

{products_summary}

For each product, provide enriched data:
- name: Clean product name
- source: Original source (tiktok/amazon/aliexpress/google_trends)
- image_url: Keep the original image_url from the scraped data if available, otherwise leave empty
- estimated_views: Estimated viral reach (use trend_data if available)
- source_cost: Estimated supplier cost from AliExpress (number, use trend_data.price if available)
- recommended_price: Recommended selling price (3-4x source cost) (number)
- margin_percent: Profit margin percentage (number)
- trend_score: How strong the trend is 1-100 (number)
- overall_score: Overall dropshipping opportunity 1-100 (number)
- category: Product category
- why_trending: Brief reason why it's trending
- saturation_level: low/medium/high based on competition
- active_fb_ads: Estimated number of Facebook ads (number)
- trend_direction: up/down/stable
{filter_instructions}

Return as JSON: {{"products": [...]}}"""
        else:
            # No scraper data - ask AI to identify trending products from its knowledge
            system_prompt = """You are a dropshipping product research expert with knowledge of current trending products.
You MUST respond with a JSON object containing a "products" array."""

            user_prompt = f"""Identify 5-8 currently trending products that would be excellent for dropshipping.

For each product provide:
- name: Product name
- source: Where it's trending (tiktok/amazon/aliexpress/google_trends)
- image_url: Keep the original image_url from the scraped data if available, otherwise leave empty
- estimated_views: Estimated viral reach (number)
- source_cost: Estimated cost from AliExpress/supplier (number)
- recommended_price: Recommended selling price (number)
- margin_percent: Profit margin percentage (number)
- trend_score: How strong the trend is 1-100 (number)
- overall_score: Overall opportunity 1-100 (number)
- category: Product category
- why_trending: Brief reason why it's trending
- saturation_level: low/medium/high
- active_fb_ads: Estimated Facebook ads count (number)
- trend_direction: up/down/stable
{filter_instructions}

Return as JSON: {{"products": [...]}}"""

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
            # Return raw scraped data without AI enrichment
            if raw_products:
                return {
                    "success": True,
                    "products": raw_products[:10],
                    "count": len(raw_products[:10]),
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
Analyze the real scraped data and enrich it with scores and recommendations.
You MUST respond with a JSON object containing a "products" array."""

            user_prompt = f"""Real scraped data from {source}:

{products_summary}

Enrich each product with:
- name, source ("{source}"), image_url (keep from scraped data if available, otherwise leave empty),estimated_views, source_cost, recommended_price
- margin_percent, trend_score (1-100), overall_score (1-100), category
- why_trending, saturation_level (low/medium/high), trend_direction (up/down/stable)
{filter_instructions}

Return as JSON: {{"products": [...]}}"""
        else:
            system_prompt = f"""You are a dropshipping expert specializing in {source} trends.
You MUST respond with a JSON object containing a "products" array."""

            user_prompt = f"""{source_prompts.get(source, 'Find trending products.')}

Identify 5-8 trending products from {source}.
{filter_instructions}

For each: name, source ("{source}"), image_url (keep from scraped data if available, otherwise leave empty),estimated_views, source_cost, recommended_price,
margin_percent, trend_score (1-100), overall_score (1-100), category, trend_data, why_trending

Return as JSON: {{"products": [...]}}"""

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
                return {
                    "success": True,
                    "source": source,
                    "products": raw_products[:8],
                    "count": len(raw_products[:8]),
                    "ai_enrichment_failed": True,
                    "scanned_at": datetime.now(timezone.utc).isoformat(),
                }
            return {"success": False, "source": source, "error": str(e), "products": [], "count": 0}

    async def analyze_product(self, product_name: str) -> Dict[str, Any]:
        """Deep analysis of a specific product with real competition data"""
        # Get real competition data from Meta Ad Library and supplier data
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
            # Merge in real data
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
        """Validate and clean a product dict, ensuring required numeric fields"""
        if not product or not product.get("name"):
            return None

        try:
            name = str(product.get("name", "Unknown"))[:100]
            # Use image_url from scraper data or AI response
            image_url = product.get("image_url", "")

            return {
                "name": name,
                "image_url": image_url,
                "source": str(product.get("source", "unknown")),
                "estimated_views": int(product.get("estimated_views", 0) or 0),
                "source_cost": float(product.get("source_cost", 0) or 0),
                "recommended_price": float(product.get("recommended_price", 0) or 0),
                "margin_percent": float(product.get("margin_percent", 0) or 0),
                "trend_score": max(0, min(100, int(product.get("trend_score", 50) or 50))),
                "overall_score": max(0, min(100, int(product.get("overall_score", 50) or 50))),
                "category": str(product.get("category", "General"))[:50],
                "why_trending": str(product.get("why_trending", ""))[:200],
                "saturation_level": str(product.get("saturation_level", "medium")),
                "active_fb_ads": int(product.get("active_fb_ads", 0) or 0),
                "trend_direction": str(product.get("trend_direction", "stable")),
                "trend_data": product.get("trend_data", {}),
            }
        except (ValueError, TypeError) as e:
            logger.warning(f"Product validation failed: {e} - {product.get('name', 'unknown')}")
            return None


def create_scanner(openai_key: str) -> AIProductScanner:
    """Factory function to create scanner with user's key"""
    return AIProductScanner(openai_key)
