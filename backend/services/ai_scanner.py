"""
AI Product Scanner - Uses OpenAI to analyze and discover trending products
Production-ready approach without browser automation
"""
import asyncio
import json
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI

class AIProductScanner:
    """
    AI-powered product scanner using OpenAI for analysis.
    More reliable than browser automation for production.
    """
    
    def __init__(self, openai_key: str):
        self.client = AsyncOpenAI(api_key=openai_key)
        self.model = "gpt-4o"
    
    async def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Make OpenAI API call"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
    
    def _parse_json_response(self, response: str) -> List[Dict]:
        """Extract JSON from response"""
        try:
            # Try to find JSON array in response
            json_match = re.search(r'\[[\s\S]*\]', response)
            if json_match:
                return json.loads(json_match.group())
            return []
        except:
            return []
    
    async def scan_trending_products(self, filters: Dict = None) -> Dict[str, Any]:
        """
        Use AI to identify currently trending products across platforms
        """
        filter_instructions = ""
        if filters:
            if filters.get("min_price"):
                filter_instructions += f"\n- Only include products likely priced above ${filters['min_price']}"
            if filters.get("max_price"):
                filter_instructions += f"\n- Only include products likely priced below ${filters['max_price']}"
            if filters.get("categories"):
                filter_instructions += f"\n- Focus on these categories: {', '.join(filters['categories'])}"
            if filters.get("excluded_terms"):
                filter_instructions += f"\n- Exclude products containing: {', '.join(filters['excluded_terms'])}"
        
        system_prompt = """You are a dropshipping product research expert. Your job is to identify trending, viral products that would be good for dropshipping stores.

You have extensive knowledge of:
- TikTok viral products and #tiktokmademebuyit trends
- Amazon Movers & Shakers
- AliExpress trending products
- Google Trends rising searches for products

Return ONLY a valid JSON array of products, no other text."""

        user_prompt = f"""Identify 5-8 currently trending products that would be excellent for dropshipping in 2026.

For each product provide:
- name: Product name
- source: Where it's trending (tiktok/amazon/aliexpress/google_trends)
- estimated_views: Estimated viral reach (number)
- source_cost: Estimated cost from AliExpress/supplier (number)
- recommended_price: Recommended selling price (number)
- margin_percent: Profit margin percentage (number)
- trend_score: How strong the trend is 1-100 (number)
- category: Product category
- why_trending: Brief reason why it's trending
{filter_instructions}

Return as JSON array:
[{{"name": "...", "source": "...", "estimated_views": 10000000, "source_cost": 5.00, "recommended_price": 29.99, "margin_percent": 83, "trend_score": 85, "category": "...", "why_trending": "..."}}]"""

        try:
            response = await self._call_openai(system_prompt, user_prompt)
            products = self._parse_json_response(response)
            
            # Add metadata to each product
            for p in products:
                p["discovered_at"] = datetime.now(timezone.utc).isoformat()
                p["ai_generated"] = True
            
            return {
                "success": True,
                "products": products,
                "count": len(products),
                "scanned_at": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e), "products": [], "count": 0}
    
    async def scan_source(self, source: str, filters: Dict = None) -> Dict[str, Any]:
        """Scan a specific source for trending products"""
        
        source_prompts = {
            "tiktok": "Focus on products going viral on TikTok with hashtags like #tiktokmademebuyit, #amazonfinds, #viralproducts. These should have 10M+ views potential.",
            "amazon": "Focus on products from Amazon Movers & Shakers - items with biggest rank increases in the past 24 hours across categories like Electronics, Home & Kitchen, Beauty.",
            "aliexpress": "Focus on hot-selling products on AliExpress with high order counts (1000+), good ratings (4.5+), and prices under $20 that have dropshipping potential.",
            "google_trends": "Focus on rising search terms related to physical products. Look for breakout searches and terms with +100% growth or higher."
        }
        
        filter_instructions = ""
        if filters:
            if filters.get("min_price"):
                filter_instructions += f"\n- Only products above ${filters['min_price']}"
            if filters.get("max_price"):
                filter_instructions += f"\n- Only products below ${filters['max_price']}"
            if filters.get("categories"):
                filter_instructions += f"\n- Categories: {', '.join(filters['categories'])}"
        
        system_prompt = f"""You are a dropshipping product research expert specializing in {source} trends.
Return ONLY a valid JSON array of products, no other text."""

        user_prompt = f"""{source_prompts.get(source, 'Find trending products.')}

Identify 5-8 trending products from {source}.
{filter_instructions}

For each product provide:
- name: Product name
- source: "{source}"
- estimated_views: Estimated reach/orders (number)
- source_cost: Supplier cost estimate (number)
- recommended_price: Sell price (number)
- margin_percent: Margin % (number)
- trend_score: 1-100 (number)
- category: Category
- trend_data: {{relevant metrics for this source}}

Return as JSON array only."""

        try:
            response = await self._call_openai(system_prompt, user_prompt)
            products = self._parse_json_response(response)
            
            for p in products:
                p["discovered_at"] = datetime.now(timezone.utc).isoformat()
                p["ai_generated"] = True
            
            return {
                "success": True,
                "source": source,
                "products": products,
                "count": len(products),
                "scanned_at": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {"success": False, "source": source, "error": str(e), "products": [], "count": 0}
    
    async def analyze_product(self, product_name: str) -> Dict[str, Any]:
        """Deep analysis of a specific product"""
        
        system_prompt = """You are a dropshipping competition analyst. Analyze products for market viability.
Return ONLY valid JSON, no other text."""

        user_prompt = f"""Analyze "{product_name}" for dropshipping potential:

Provide:
- competition_level: low/medium/high
- estimated_fb_ads: Number of Facebook ads running for this product
- saturation_score: 1-100 (100 = very saturated)
- recommendation: "launch" / "caution" / "avoid"
- supplier_estimate: Estimated AliExpress cost
- recommended_price: Suggested selling price
- target_audience: Who to target
- ad_angles: 3 potential ad angles/hooks
- risks: Potential risks
- opportunity_score: 1-100 overall opportunity

Return as JSON object."""

        try:
            response = await self._call_openai(system_prompt, user_prompt)
            # Parse JSON object
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                analysis = {"error": "Could not parse response"}
            
            return {
                "success": True,
                "product_name": product_name,
                "analysis": analysis,
                "analyzed_at": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {"success": False, "product_name": product_name, "error": str(e)}
    
    async def run_full_scan(self, filters: Dict = None) -> Dict[str, Any]:
        """Run full scan across all sources"""
        
        results = await asyncio.gather(
            self.scan_source("tiktok", filters),
            self.scan_source("amazon", filters),
            self.scan_source("aliexpress", filters),
            self.scan_source("google_trends", filters),
            return_exceptions=True
        )
        
        all_products = []
        source_stats = {}
        
        sources = ["tiktok", "amazon", "aliexpress", "google_trends"]
        for i, source in enumerate(sources):
            if isinstance(results[i], dict) and results[i].get("success"):
                products = results[i].get("products", [])
                all_products.extend(products)
                source_stats[source] = len(products)
            else:
                source_stats[source] = 0
        
        # Sort by trend_score
        all_products.sort(key=lambda x: x.get("trend_score", 0), reverse=True)
        
        return {
            "success": True,
            "total_products": len(all_products),
            "products": all_products,
            "source_stats": source_stats,
            "scan_mode": "ai_powered",
            "scanned_at": datetime.now(timezone.utc).isoformat()
        }


def create_scanner(openai_key: str) -> AIProductScanner:
    """Factory function to create scanner with user's key"""
    return AIProductScanner(openai_key)
