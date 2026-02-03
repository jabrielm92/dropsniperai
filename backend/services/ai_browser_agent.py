"""
AI Browser Agent - Uses browser-use library to autonomously browse websites
Like the original ClawdBot concept - AI controls browser like a human
"""
import asyncio
import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Check if browser-use and dependencies are available
BROWSER_USE_AVAILABLE = False
try:
    from browser_use import Agent
    from langchain_openai import ChatOpenAI
    BROWSER_USE_AVAILABLE = True
except ImportError:
    pass


class AIBrowserAgent:
    """
    AI-powered browser agent that autonomously browses websites.
    Replicates the ClawdBot approach from the original X post.
    """
    
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.is_configured = bool(self.openai_key) and BROWSER_USE_AVAILABLE
        
    def _get_llm(self):
        """Get the LLM instance for browser-use"""
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY not configured")
        return ChatOpenAI(model="gpt-4o", api_key=self.openai_key)
    
    async def scan_tiktok_trending(self) -> Dict[str, Any]:
        """
        Browse TikTok and find trending product hashtags with 10M+ views
        """
        if not self.is_configured:
            return {"error": "Agent not configured", "fallback": True}
        
        task = """
        Go to TikTok.com and search for trending product-related content:
        1. Search for hashtag #tiktokmademebuyit
        2. Look at the top 5-10 videos with the most views
        3. For each video, note:
           - The product being shown (if any)
           - Approximate view count
           - The main hashtags used
        4. Also check hashtags: #amazonfinds, #viralproducts
        5. Return a JSON list of trending products found with format:
           [{"name": "product name", "views": "estimated views", "hashtags": ["tag1", "tag2"]}]
        Only include products that appear to have 10M+ combined views.
        """
        
        try:
            agent = Agent(task=task, llm=self._get_llm())
            result = await agent.run()
            return {
                "source": "tiktok",
                "raw_result": str(result),
                "scanned_at": datetime.now(timezone.utc).isoformat(),
                "success": True
            }
        except Exception as e:
            return {"source": "tiktok", "error": str(e), "success": False}
    
    async def scan_amazon_movers(self) -> Dict[str, Any]:
        """
        Browse Amazon Movers & Shakers for trending products
        """
        if not self.is_configured:
            return {"error": "Agent not configured", "fallback": True}
        
        task = """
        Go to Amazon.com and navigate to "Movers & Shakers":
        1. Go to amazon.com
        2. Find and click on "Best Sellers" or navigate to the Movers & Shakers section
        3. Look at multiple categories: Electronics, Home & Kitchen, Beauty, Sports
        4. For each category, find the top 3-5 products with biggest rank increases
        5. Note for each product:
           - Product name
           - Price
           - Rank change percentage
           - Category
        6. Return a JSON list with format:
           [{"name": "product", "price": "$XX.XX", "rank_change": "+XX%", "category": "category name"}]
        Focus on products under $50 that show significant rank increases.
        """
        
        try:
            agent = Agent(task=task, llm=self._get_llm())
            result = await agent.run()
            return {
                "source": "amazon",
                "raw_result": str(result),
                "scanned_at": datetime.now(timezone.utc).isoformat(),
                "success": True
            }
        except Exception as e:
            return {"source": "amazon", "error": str(e), "success": False}
    
    async def scan_aliexpress_trending(self) -> Dict[str, Any]:
        """
        Browse AliExpress for trending/hot products
        """
        if not self.is_configured:
            return {"error": "Agent not configured", "fallback": True}
        
        task = """
        Go to AliExpress.com and find trending products:
        1. Go to aliexpress.com
        2. Look for "Top Selling", "Hot Products", or "Trending" sections
        3. Browse categories like Electronics, Home, Fashion accessories
        4. For products that appear popular (high order counts), note:
           - Product name
           - Price in USD
           - Number of orders (if visible)
           - Rating (if visible)
        5. Return a JSON list with format:
           [{"name": "product", "price": X.XX, "orders": "XX,XXX", "rating": X.X}]
        Focus on products priced under $20 with high order counts (1000+).
        """
        
        try:
            agent = Agent(task=task, llm=self._get_llm())
            result = await agent.run()
            return {
                "source": "aliexpress",
                "raw_result": str(result),
                "scanned_at": datetime.now(timezone.utc).isoformat(),
                "success": True
            }
        except Exception as e:
            return {"source": "aliexpress", "error": str(e), "success": False}
    
    async def scan_google_trends(self) -> Dict[str, Any]:
        """
        Browse Google Trends for rising product-related searches
        """
        if not self.is_configured:
            return {"error": "Agent not configured", "fallback": True}
        
        task = """
        Go to Google Trends and find rising product-related searches:
        1. Go to trends.google.com
        2. Look at "Trending Searches" or "Year in Search"
        3. Search for product-related terms like "buy", "best", gadgets, accessories
        4. For rising search terms that relate to purchasable products, note:
           - Search term
           - Growth indicator (rising, breakout, percentage)
           - Related topics
        5. Return a JSON list with format:
           [{"term": "search term", "growth": "rising/breakout/+XX%", "related": ["topic1", "topic2"]}]
        Focus on terms that indicate buying intent for physical products.
        """
        
        try:
            agent = Agent(task=task, llm=self._get_llm())
            result = await agent.run()
            return {
                "source": "google_trends",
                "raw_result": str(result),
                "scanned_at": datetime.now(timezone.utc).isoformat(),
                "success": True
            }
        except Exception as e:
            return {"source": "google_trends", "error": str(e), "success": False}
    
    async def scan_meta_ad_library(self, product_name: str) -> Dict[str, Any]:
        """
        Browse Meta Ad Library to analyze competition for a product
        """
        if not self.is_configured:
            return {"error": "Agent not configured", "fallback": True}
        
        task = f"""
        Go to Meta Ad Library and research ads for "{product_name}":
        1. Go to facebook.com/ads/library
        2. Search for "{product_name}" 
        3. Filter by "All ads" and country "United States"
        4. Count approximately how many active ads exist
        5. Look at the top advertisers running these ads
        6. Note common ad themes, hooks, or angles being used
        7. Return a JSON object with format:
           {{"product": "{product_name}", "total_ads": XX, "top_advertisers": ["name1", "name2"], "common_hooks": ["hook1", "hook2"]}}
        """
        
        try:
            agent = Agent(task=task, llm=self._get_llm())
            result = await agent.run()
            return {
                "source": "meta_ads",
                "product": product_name,
                "raw_result": str(result),
                "scanned_at": datetime.now(timezone.utc).isoformat(),
                "success": True
            }
        except Exception as e:
            return {"source": "meta_ads", "error": str(e), "success": False}
    
    async def scan_competitor_store(self, store_url: str) -> Dict[str, Any]:
        """
        Browse a competitor's store and extract product listings
        """
        if not self.is_configured:
            return {"error": "Agent not configured", "fallback": True}
        
        task = f"""
        Go to the online store at {store_url} and analyze their products:
        1. Navigate to {store_url}
        2. Browse through their product catalog/collections
        3. For each product you can find, note:
           - Product name
           - Price
           - Whether it appears to be featured or best-selling
        4. Count total number of products visible
        5. Note the main product categories they sell
        6. Return a JSON object with format:
           {{"store_url": "{store_url}", "products": [{{"name": "product", "price": XX.XX}}], "total_products": XX, "categories": ["cat1", "cat2"]}}
        """
        
        try:
            agent = Agent(task=task, llm=self._get_llm())
            result = await agent.run()
            return {
                "source": "competitor_store",
                "store_url": store_url,
                "raw_result": str(result),
                "scanned_at": datetime.now(timezone.utc).isoformat(),
                "success": True
            }
        except Exception as e:
            return {"source": "competitor_store", "error": str(e), "success": False}
    
    async def run_full_scan(self) -> Dict[str, Any]:
        """
        Run a complete scan across all sources
        """
        if not self.is_configured:
            return {
                "error": "AI Browser Agent not configured. Add OPENAI_API_KEY to enable.",
                "configured": False,
                "fallback": True
            }
        
        results = await asyncio.gather(
            self.scan_tiktok_trending(),
            self.scan_amazon_movers(),
            self.scan_aliexpress_trending(),
            self.scan_google_trends(),
            return_exceptions=True
        )
        
        scan_results = {
            "tiktok": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
            "amazon": results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])},
            "aliexpress": results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])},
            "google_trends": results[3] if not isinstance(results[3], Exception) else {"error": str(results[3])},
        }
        
        return {
            "scan_type": "full_ai_browser",
            "results": scan_results,
            "scanned_at": datetime.now(timezone.utc).isoformat(),
            "configured": True
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get the configuration status of the AI browser agent"""
        return {
            "browser_use_available": BROWSER_USE_AVAILABLE,
            "openai_key_configured": bool(self.openai_key),
            "is_ready": self.is_configured,
            "message": "Ready to browse" if self.is_configured else "Add OPENAI_API_KEY to enable AI browsing"
        }


# Singleton instance
ai_browser_agent = AIBrowserAgent()
