"""
Product Scout Services - Real Web Scrapers
Scrapes Amazon, AliExpress, TikTok Creative Center, Meta Ad Library, and Google Trends
using httpx + BeautifulSoup for lightweight HTTP-based scraping.

Key improvements:
- Multiple fallback strategies per source (API -> mobile -> HTML -> RSS)
- Better anti-detection headers (realistic Accept, Referer, sec-ch-ua)
- Longer timeouts and retry logic
- AliExpress mobile API endpoint for reliable JSON data
- Amazon Best Sellers RSS feed as primary source
- TikTok keyword-based Creative Center API
"""
import asyncio
import logging
import re
import json
import random
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus, urlencode

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Rotating user agents - modern Chrome versions for 2026
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
]

def _get_headers(idx: int = 0) -> Dict[str, str]:
    ua = USER_AGENTS[idx % len(USER_AGENTS)]
    return {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "sec-ch-ua": '"Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

def _get_api_headers() -> Dict[str, str]:
    """Headers for JSON API endpoints"""
    ua = random.choice(USER_AGENTS)
    return {
        "User-Agent": ua,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "sec-ch-ua": '"Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }


class TikTokScanner:
    """Scrapes TikTok Creative Center for trending products and hashtags.

    Strategy:
    1. Try Creative Center hashtag API (returns JSON)
    2. Try Creative Center keyword/product API
    3. Fallback: scrape Creative Center trending page HTML
    """

    CREATIVE_CENTER_URL = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en"
    HASHTAG_API = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list"
    KEYWORD_API = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/keyword/list"
    PRODUCT_API = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/product/list"

    async def scan_trending(self, niche: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scan TikTok Creative Center for trending hashtags related to products"""
        products = []

        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            # Strategy 1: Creative Center hashtag API
            products = await self._try_hashtag_api(client)

            # Strategy 2: Creative Center keyword API
            if not products:
                products = await self._try_keyword_api(client)

            # Strategy 3: Scrape Creative Center trending page
            if not products:
                products = await self._try_trending_page(client)

            # Strategy 4: Scrape TikTok tag pages with product hashtags
            if not products:
                products = await self._try_tag_pages(client)

        logger.info(f"TikTok scanner found {len(products)} products")
        return products[:12]

    async def _try_hashtag_api(self, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """Try the Creative Center hashtag list API"""
        products = []
        try:
            for period in [7, 30]:  # Try weekly then monthly
                resp = await client.get(
                    self.HASHTAG_API,
                    params={
                        "page": 1,
                        "limit": 50,
                        "period": period,
                        "country_code": "US",
                        "sort_by": "popular",
                    },
                    headers={
                        **_get_api_headers(),
                        "Referer": self.CREATIVE_CENTER_URL,
                        "Origin": "https://ads.tiktok.com",
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    product_kw = [
                        "buy", "find", "product", "gadget", "must", "hack", "deal",
                        "clean", "home", "kitchen", "beauty", "fitness", "tech", "gift",
                        "amazon", "shop", "unbox", "review", "haul", "worth", "best",
                        "tool", "organiz", "storage", "lamp", "light", "phone", "car",
                        "skincare", "makeup", "viral", "trending", "tiktok", "dropship",
                    ]
                    for item in data.get("data", {}).get("list", []):
                        name = item.get("hashtag_name", "")
                        if any(kw in name.lower() for kw in product_kw):
                            products.append({
                                "source": "tiktok",
                                "name": name.replace("#", "").replace("_", " ").title(),
                                "trend_data": {
                                    "hashtag": f"#{name}",
                                    "views": item.get("publish_cnt", 0),
                                    "growth_rate": item.get("trend", 0),
                                    "video_count": item.get("video_cnt", 0),
                                },
                                "discovered_at": datetime.now(timezone.utc).isoformat(),
                            })
                    if products:
                        logger.info(f"TikTok: hashtag API returned {len(products)} products (period={period})")
                        break
                await asyncio.sleep(0.5)
        except Exception as e:
            logger.warning(f"TikTok hashtag API failed: {e}")
        return products

    async def _try_keyword_api(self, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """Try the Creative Center keyword trends API"""
        products = []
        try:
            resp = await client.get(
                self.KEYWORD_API,
                params={
                    "page": 1,
                    "limit": 30,
                    "period": 7,
                    "country_code": "US",
                    "sort_by": "popular",
                    "industry_id": "",  # All industries
                },
                headers={
                    **_get_api_headers(),
                    "Referer": "https://ads.tiktok.com/business/creativecenter/inspiration/popular/keyword/pc/en",
                    "Origin": "https://ads.tiktok.com",
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("data", {}).get("list", []):
                    kw = item.get("keyword", "")
                    if kw and len(kw) > 3:
                        products.append({
                            "source": "tiktok",
                            "name": kw.title(),
                            "trend_data": {
                                "keyword": kw,
                                "views": item.get("video_views", 0),
                                "growth_rate": item.get("trend", 0),
                                "video_count": item.get("video_cnt", 0),
                                "ctr": item.get("ctr", 0),
                            },
                            "discovered_at": datetime.now(timezone.utc).isoformat(),
                        })
                if products:
                    logger.info(f"TikTok: keyword API returned {len(products)} results")
        except Exception as e:
            logger.warning(f"TikTok keyword API failed: {e}")
        return products

    async def _try_trending_page(self, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """Scrape TikTok Creative Center trending page HTML"""
        products = []
        try:
            # Try the product-specific trending page
            urls = [
                "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en",
                "https://ads.tiktok.com/business/creativecenter/inspiration/popular/product/pc/en",
            ]
            for url in urls:
                resp = await client.get(url, headers=_get_headers(0))
                if resp.status_code == 200:
                    text = resp.text
                    # Look for embedded JSON data in script tags
                    json_matches = re.findall(r'window\.__INITIAL_PROPS__\s*=\s*({.+?})\s*;', text, re.DOTALL)
                    if not json_matches:
                        json_matches = re.findall(r'"hashtag_name"\s*:\s*"([^"]+)"', text)
                        for name in json_matches[:10]:
                            products.append({
                                "source": "tiktok",
                                "name": name.replace("_", " ").title(),
                                "trend_data": {"hashtag": f"#{name}", "views": 0, "growth_rate": 0},
                                "discovered_at": datetime.now(timezone.utc).isoformat(),
                            })
                    if products:
                        break
                await asyncio.sleep(0.5)
        except Exception as e:
            logger.warning(f"TikTok trending page scrape failed: {e}")
        return products

    async def _try_tag_pages(self, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """Scrape individual TikTok tag pages"""
        products = []
        product_hashtags = [
            "tiktokmademebuyit", "amazonfinds", "viralproducts",
            "musthave", "gadgettok", "homeessentials", "cleaningtok",
        ]
        for tag in product_hashtags[:4]:
            try:
                resp = await client.get(
                    f"https://www.tiktok.com/tag/{tag}",
                    headers=_get_headers(1),
                )
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    meta = soup.find("meta", {"property": "og:description"})
                    view_text = meta.get("content", "") if meta else ""
                    views = _parse_view_count(view_text)

                    # Try JSON-LD scripts
                    for script in soup.find_all("script", {"type": "application/ld+json"})[:5]:
                        try:
                            ld = json.loads(script.string or "{}")
                            desc = ld.get("description", "") or ld.get("name", "")
                            if desc and len(desc) > 10:
                                products.append({
                                    "source": "tiktok",
                                    "name": _extract_product_name(desc, tag),
                                    "trend_data": {"hashtag": f"#{tag}", "views": views, "growth_rate": 0},
                                    "discovered_at": datetime.now(timezone.utc).isoformat(),
                                })
                        except (json.JSONDecodeError, AttributeError):
                            pass

                    # Try __UNIVERSAL_DATA_FOR_REHYDRATION__ for video descriptions
                    for script in soup.find_all("script"):
                        text = script.string or ""
                        if "__UNIVERSAL_DATA_FOR_REHYDRATION__" in text or "SIGI_STATE" in text:
                            desc_matches = re.findall(r'"desc"\s*:\s*"([^"]{10,80})"', text)
                            for desc in desc_matches[:5]:
                                products.append({
                                    "source": "tiktok",
                                    "name": _extract_product_name(desc, tag),
                                    "trend_data": {"hashtag": f"#{tag}", "views": views, "growth_rate": 0},
                                    "discovered_at": datetime.now(timezone.utc).isoformat(),
                                })
                            if desc_matches:
                                break
                await asyncio.sleep(1)
            except Exception as e:
                logger.warning(f"TikTok tag scrape failed for #{tag}: {e}")
        return products


class AmazonScanner:
    """Scrapes Amazon for trending products.

    Strategy:
    1. Amazon Best Sellers RSS feeds (XML, no JS required)
    2. Amazon Best Sellers HTML pages with multiple selector strategies
    3. Amazon Movers & Shakers pages
    """

    # RSS feeds for Amazon Best Sellers - these return XML, no JS rendering needed
    BESTSELLER_RSS = {
        "Electronics": "https://www.amazon.com/gp/rss/bestsellers/electronics",
        "Home & Kitchen": "https://www.amazon.com/gp/rss/bestsellers/home-garden",
        "Beauty": "https://www.amazon.com/gp/rss/bestsellers/beauty",
        "Sports & Outdoors": "https://www.amazon.com/gp/rss/bestsellers/sporting-goods",
        "Health & Personal Care": "https://www.amazon.com/gp/rss/bestsellers/hpc",
        "Pet Supplies": "https://www.amazon.com/gp/rss/bestsellers/pet-supplies",
    }

    MOVERS_URLS = {
        "Electronics": "https://www.amazon.com/gp/movers-and-shakers/electronics",
        "Home & Kitchen": "https://www.amazon.com/gp/movers-and-shakers/home-garden",
        "Beauty": "https://www.amazon.com/gp/movers-and-shakers/beauty",
        "Sports & Outdoors": "https://www.amazon.com/gp/movers-and-shakers/sporting-goods",
        "Health & Personal Care": "https://www.amazon.com/gp/movers-and-shakers/hpc",
        "Pet Supplies": "https://www.amazon.com/gp/movers-and-shakers/pet-supplies",
    }

    BESTSELLER_URLS = {
        "Electronics": "https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics",
        "Home & Kitchen": "https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/home-garden",
        "Beauty": "https://www.amazon.com/Best-Sellers-Beauty-Personal-Care/zgbs/beauty",
    }

    async def scan_movers_shakers(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get trending Amazon products using multiple strategies"""
        products = []

        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            # Strategy 1: RSS feeds (most reliable - returns XML, not blocked)
            products = await self._try_rss_feeds(client, category)

            # Strategy 2: Best Sellers HTML pages
            if not products:
                products = await self._try_bestseller_pages(client, category)

            # Strategy 3: Movers & Shakers pages
            if not products:
                products = await self._try_movers_pages(client, category)

        logger.info(f"Amazon scanner found {len(products)} products")
        return products[:15]

    async def _try_rss_feeds(self, client: httpx.AsyncClient, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Parse Amazon Best Sellers RSS feeds (XML format, very reliable)"""
        products = []
        feeds = {}

        if category and category in self.BESTSELLER_RSS:
            feeds = {category: self.BESTSELLER_RSS[category]}
        else:
            for cat in ["Electronics", "Home & Kitchen", "Beauty"]:
                feeds[cat] = self.BESTSELLER_RSS[cat]

        for cat_name, feed_url in feeds.items():
            try:
                resp = await client.get(feed_url, headers={
                    "User-Agent": random.choice(USER_AGENTS),
                    "Accept": "application/rss+xml, application/xml, text/xml, */*",
                })
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "xml")
                    items = soup.find_all("item")
                    if not items:
                        # Try HTML parser as fallback for RSS
                        soup = BeautifulSoup(resp.text, "html.parser")
                        items = soup.find_all("item")

                    for item in items[:8]:
                        title = item.find("title")
                        if not title:
                            continue
                        name = title.get_text(strip=True)
                        if not name or len(name) < 3:
                            continue

                        # Clean up Amazon RSS title format: "#1: Product Name"
                        name = re.sub(r'^#?\d+[\s:.-]+', '', name).strip()
                        if not name:
                            continue

                        # Extract price from description
                        desc = item.find("description")
                        desc_text = desc.get_text(strip=True) if desc else ""
                        price = _parse_price(desc_text) if desc_text else 0

                        # Extract image from description HTML
                        image_url = ""
                        if desc and desc.string:
                            img_match = re.search(r'<img[^>]+src="([^"]+)"', desc.string or desc_text)
                            if img_match:
                                image_url = img_match.group(1)

                        products.append({
                            "source": "amazon",
                            "name": name[:100],
                            "image_url": image_url,
                            "trend_data": {
                                "rank_change": 0,
                                "category": cat_name,
                                "current_price": price,
                                "source_type": "bestseller_rss",
                            },
                            "discovered_at": datetime.now(timezone.utc).isoformat(),
                        })

                    if products:
                        logger.info(f"Amazon: RSS feed returned {len(products)} for {cat_name}")

                await asyncio.sleep(0.5)
            except Exception as e:
                logger.warning(f"Amazon RSS feed failed for {cat_name}: {e}")
        return products

    async def _try_bestseller_pages(self, client: httpx.AsyncClient, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scrape Amazon Best Sellers HTML pages"""
        products = []
        urls = {}
        if category and category in self.BESTSELLER_URLS:
            urls = {category: self.BESTSELLER_URLS[category]}
        else:
            urls = dict(list(self.BESTSELLER_URLS.items())[:3])

        for cat_name, url in urls.items():
            try:
                resp = await client.get(url, headers=_get_headers(2))
                if resp.status_code == 200:
                    products.extend(self._parse_amazon_html(resp.text, cat_name, "bestseller"))
                await asyncio.sleep(1)
            except Exception as e:
                logger.warning(f"Amazon bestseller page failed for {cat_name}: {e}")
        return products

    async def _try_movers_pages(self, client: httpx.AsyncClient, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scrape Amazon Movers & Shakers pages"""
        products = []
        urls = {}
        if category and category in self.MOVERS_URLS:
            urls = {category: self.MOVERS_URLS[category]}
        else:
            for cat in ["Electronics", "Home & Kitchen", "Beauty"]:
                urls[cat] = self.MOVERS_URLS[cat]

        for cat_name, url in urls.items():
            try:
                resp = await client.get(url, headers=_get_headers(2))
                if resp.status_code == 200:
                    products.extend(self._parse_amazon_html(resp.text, cat_name, "movers"))
                await asyncio.sleep(1)
            except Exception as e:
                logger.warning(f"Amazon movers page failed for {cat_name}: {e}")
        return products

    def _parse_amazon_html(self, html: str, cat_name: str, source_type: str) -> List[Dict[str, Any]]:
        """Parse Amazon HTML with multiple selector strategies"""
        products = []
        soup = BeautifulSoup(html, "html.parser")

        # Strategy A: Standard grid items
        items = soup.select("#zg-ordered-list li, .zg-item-immersion")

        # Strategy B: Data-asin divs
        if not items:
            items = soup.select("div[data-asin], div[id*='gridItem']")

        # Strategy C: Product links with /dp/
        if not items:
            links = soup.select("a[href*='/dp/']")
            seen_names = set()
            for link in links[:15]:
                name = link.get_text(strip=True)
                if name and 5 < len(name) < 200 and name not in seen_names:
                    seen_names.add(name)
                    parent = link.find_parent("div")
                    img_el = parent.select_one("img[src]") if parent else None
                    image_url = img_el.get("src", "") if img_el else ""
                    price = 0
                    price_el = parent.select_one(".a-price .a-offscreen, span.a-price span") if parent else None
                    if price_el:
                        price = _parse_price(price_el.get_text(strip=True))

                    products.append({
                        "source": "amazon",
                        "name": name[:100],
                        "image_url": image_url,
                        "trend_data": {
                            "rank_change": 0,
                            "category": cat_name,
                            "current_price": price,
                            "source_type": source_type,
                        },
                        "discovered_at": datetime.now(timezone.utc).isoformat(),
                    })

        # Parse standard items
        for item in items[:8]:
            name_el = item.select_one(
                ".zg-text-center-align, ._cDEzb_p13n-sc-css-line-clamp-1_1Fn1y, "
                ".p13n-sc-truncate, a[href*='/dp/'], "
                "span[class*='truncate'], div[class*='truncate'], "
                ".a-link-normal span"
            )
            price_el = item.select_one(
                ".p13n-sc-price, ._cDEzb_p13n-sc-price_3mJ9Z, "
                ".a-price .a-offscreen, span.a-price span"
            )
            img_el = item.select_one("img[src]")

            name = name_el.get_text(strip=True) if name_el else None
            if not name or len(name) < 3:
                continue

            price = _parse_price(price_el.get_text(strip=True)) if price_el else 0
            image_url = img_el.get("src", "") if img_el else ""

            rank_change = 0
            percent_el = item.select_one(".zg-percent-change, .a-size-small")
            if percent_el:
                try:
                    rank_change = int(re.sub(r'[^\d]', '', percent_el.get_text(strip=True)) or 0)
                except ValueError:
                    pass

            products.append({
                "source": "amazon",
                "name": name[:100],
                "image_url": image_url,
                "trend_data": {
                    "rank_change": rank_change,
                    "category": cat_name,
                    "current_price": price,
                    "source_type": source_type,
                },
                "discovered_at": datetime.now(timezone.utc).isoformat(),
            })

        return products


class AliExpressScanner:
    """Scrapes AliExpress for trending/hot products with supplier data.

    Strategy:
    1. AliExpress mobile API endpoint (returns JSON, most reliable)
    2. AliExpress search page with script tag parsing
    3. AliExpress popular/hot products pages
    """

    async def scan_trending(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scrape AliExpress for hot products with supplier pricing"""
        products = []

        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            # Strategy 1: AliExpress mobile/API endpoint (JSON data)
            products = await self._try_api_search(client, category)

            # Strategy 2: Standard search page parsing
            if not products:
                products = await self._try_search_pages(client, category)

            # Strategy 3: AliExpress hot products / deals page
            if not products:
                products = await self._try_deals_page(client)

        logger.info(f"AliExpress scanner found {len(products)} products")
        return products[:15]

    async def _try_api_search(self, client: httpx.AsyncClient, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Try AliExpress search API/mobile endpoints that return JSON"""
        products = []
        search_terms = [
            "trending gadgets 2026", "viral tiktok products",
            "dropshipping hot products", "bestseller new arrivals",
        ]
        if category:
            search_terms = [f"{category} bestseller", f"{category} trending 2026"]

        for term in search_terms[:2]:
            try:
                # Try the glosearch API endpoint used by AliExpress's frontend
                api_url = "https://www.aliexpress.com/fn/search-pc/index"
                params = {
                    "SearchText": term,
                    "SortType": "total_tranpro_desc",
                    "page": 1,
                    "limit": 20,
                }
                resp = await client.get(
                    api_url,
                    params=params,
                    headers={
                        **_get_api_headers(),
                        "Referer": f"https://www.aliexpress.com/w/wholesale-{quote_plus(term)}.html",
                        "Origin": "https://www.aliexpress.com",
                    },
                )
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        items = data.get("data", {}).get("root", {}).get("fields", {}).get("mods", {}).get("itemList", {}).get("content", [])
                        if not items:
                            # Try alternate JSON structure
                            items = data.get("items", data.get("products", []))
                        for item in items[:10]:
                            title = item.get("title", {})
                            if isinstance(title, dict):
                                title = title.get("displayTitle", title.get("seoTitle", ""))
                            price_info = item.get("prices", {})
                            price = 0
                            if isinstance(price_info, dict):
                                price = float(price_info.get("salePrice", {}).get("minPrice", 0) or 0)
                            if not price:
                                price = float(item.get("price", item.get("min_price", 0)) or 0)

                            orders = int(item.get("trade", {}).get("tradeDesc", "0").replace("+", "").replace(",", "").split()[0] or 0) if isinstance(item.get("trade"), dict) else 0
                            if not orders:
                                orders = int(item.get("orders", item.get("tradeCount", 0)) or 0)

                            image = item.get("image", {})
                            if isinstance(image, dict):
                                image = image.get("imgUrl", "")
                            if isinstance(image, str) and image.startswith("//"):
                                image = "https:" + image

                            rating = float(item.get("evaluation", item.get("starRating", 0)) or 0)

                            if title and (price > 0 or orders > 0):
                                products.append({
                                    "source": "aliexpress",
                                    "name": str(title)[:100],
                                    "image_url": str(image) if image else "",
                                    "trend_data": {
                                        "orders_30d": orders,
                                        "price": price,
                                        "rating": rating,
                                        "order_velocity": round(orders / 30, 1) if orders else 0,
                                    },
                                    "discovered_at": datetime.now(timezone.utc).isoformat(),
                                })
                    except (json.JSONDecodeError, ValueError):
                        pass

                if products:
                    logger.info(f"AliExpress: API returned {len(products)} products")
                    break
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.warning(f"AliExpress API search failed for '{term}': {e}")
        return products

    async def _try_search_pages(self, client: httpx.AsyncClient, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Parse AliExpress search page HTML/script tags"""
        products = []
        search_terms = [
            "trending gadgets 2026", "viral tiktok products",
            "dropshipping hot products", "new arrivals bestseller",
        ]
        if category:
            search_terms = [f"{category} bestseller", f"{category} trending"]

        for term in search_terms[:2]:
            try:
                url = f"https://www.aliexpress.com/w/wholesale-{quote_plus(term)}.html"
                params = {"SortType": "total_tranpro_desc"}
                resp = await client.get(url, params=params, headers=_get_headers(3))

                if resp.status_code == 200:
                    text = resp.text

                    # Parse from embedded script JSON data
                    for script_pattern in [
                        r'"title":"([^"]{5,100})"',
                        r'"subject":"([^"]{5,100})"',
                        r'"displayTitle":"([^"]{5,100})"',
                    ]:
                        json_matches = re.findall(script_pattern, text)
                        if json_matches:
                            price_matches = re.findall(r'"minPrice":"?(\d+\.?\d*)"?', text)
                            order_matches = re.findall(r'"tradeCount":"?(\d+)"?', text)
                            if not order_matches:
                                order_matches = re.findall(r'"tradeDesc"\s*:\s*"(\d+)', text)
                            rating_matches = re.findall(r'"starRating":"?(\d+\.?\d*)"?', text)
                            image_matches = re.findall(r'"imgUrl"\s*:\s*"((?:https?:)?//[^"]+)"', text)

                            for i in range(min(len(json_matches), 10)):
                                name = json_matches[i]
                                price = float(price_matches[i]) if i < len(price_matches) else 0
                                orders = int(order_matches[i]) if i < len(order_matches) else 0
                                rating = float(rating_matches[i]) if i < len(rating_matches) else 0
                                image_url = image_matches[i] if i < len(image_matches) else ""
                                if image_url.startswith("//"):
                                    image_url = "https:" + image_url

                                if price > 0 and name:
                                    products.append({
                                        "source": "aliexpress",
                                        "name": name[:100],
                                        "image_url": image_url,
                                        "trend_data": {
                                            "orders_30d": orders,
                                            "price": price,
                                            "rating": rating,
                                            "order_velocity": round(orders / 30, 1) if orders else 0,
                                        },
                                        "discovered_at": datetime.now(timezone.utc).isoformat(),
                                    })
                            if products:
                                break

                    # Fallback: parse product cards directly
                    if not products:
                        soup = BeautifulSoup(text, "html.parser")
                        cards = soup.select(
                            ".list--gallery--C2f2tvm .multi--container--1UZxxHY, "
                            ".search-card-item, "
                            "[class*='product-snippet'], "
                            "[class*='search-item-card']"
                        )
                        for card in cards[:10]:
                            title_el = card.select_one(
                                ".multi--titleText--nXeOvyr, h3, "
                                "[class*='title'], [class*='subject']"
                            )
                            price_el = card.select_one(
                                ".multi--price-sale--U-S0jtj, "
                                ".search-card-e-price-main, "
                                "[class*='price']"
                            )
                            orders_el = card.select_one(
                                ".multi--trade--Ktbl2jB, "
                                ".search-card-e-review, "
                                "[class*='trade'], [class*='sold']"
                            )
                            img_el = card.select_one("img[src]")

                            title = title_el.get_text(strip=True) if title_el else None
                            if not title:
                                continue

                            price = _parse_price(price_el.get_text(strip=True)) if price_el else 0
                            orders_text = orders_el.get_text(strip=True) if orders_el else "0"
                            orders = _parse_order_count(orders_text)
                            image_url = ""
                            if img_el:
                                image_url = img_el.get("src", img_el.get("data-src", ""))
                                if image_url.startswith("//"):
                                    image_url = "https:" + image_url

                            products.append({
                                "source": "aliexpress",
                                "name": title[:100],
                                "image_url": image_url,
                                "trend_data": {
                                    "orders_30d": orders,
                                    "price": price,
                                    "rating": 0,
                                    "order_velocity": round(orders / 30, 1) if orders else 0,
                                },
                                "discovered_at": datetime.now(timezone.utc).isoformat(),
                            })

                if products:
                    break
                await asyncio.sleep(1)
            except Exception as e:
                logger.warning(f"AliExpress search page failed for '{term}': {e}")
        return products

    async def _try_deals_page(self, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """Try AliExpress deals/popular pages"""
        products = []
        deal_urls = [
            "https://www.aliexpress.com/popular.html",
            "https://www.aliexpress.com/wholesale",
        ]
        for url in deal_urls:
            try:
                resp = await client.get(url, headers=_get_headers(4))
                if resp.status_code == 200:
                    text = resp.text
                    title_matches = re.findall(r'"title":"([^"]{5,100})"', text)
                    price_matches = re.findall(r'"minPrice":"?(\d+\.?\d*)"?', text)
                    image_matches = re.findall(r'"imgUrl"\s*:\s*"((?:https?:)?//[^"]+)"', text)

                    for i in range(min(len(title_matches), 10)):
                        price = float(price_matches[i]) if i < len(price_matches) else 0
                        image_url = image_matches[i] if i < len(image_matches) else ""
                        if image_url.startswith("//"):
                            image_url = "https:" + image_url

                        if title_matches[i] and price > 0:
                            products.append({
                                "source": "aliexpress",
                                "name": title_matches[i][:100],
                                "image_url": image_url,
                                "trend_data": {
                                    "orders_30d": 0,
                                    "price": price,
                                    "rating": 0,
                                    "order_velocity": 0,
                                },
                                "discovered_at": datetime.now(timezone.utc).isoformat(),
                            })
                if products:
                    break
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.warning(f"AliExpress deals page failed: {e}")
        return products

    async def find_suppliers(self, product_name: str) -> List[Dict[str, Any]]:
        """Find suppliers for a specific product on AliExpress"""
        suppliers = []

        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            try:
                url = f"https://www.aliexpress.com/w/wholesale-{quote_plus(product_name)}.html"
                params = {"SortType": "total_tranpro_desc"}
                resp = await client.get(url, params=params, headers=_get_headers(4))

                if resp.status_code == 200:
                    text = resp.text

                    # Parse from script JSON
                    titles = re.findall(r'"title":"([^"]{5,100})"', text)
                    prices = re.findall(r'"minPrice":"?(\d+\.?\d*)"?', text)
                    orders = re.findall(r'"tradeCount":"?(\d+)"?', text)
                    ratings = re.findall(r'"starRating":"?(\d+\.?\d*)"?', text)
                    store_names = re.findall(r'"storeName":"([^"]+)"', text)
                    image_matches = re.findall(r'"imgUrl"\s*:\s*"((?:https?:)?//[^"]+)"', text)

                    for i in range(min(len(titles), 5)):
                        price = float(prices[i]) if i < len(prices) else 0
                        if price <= 0:
                            continue
                        image_url = image_matches[i] if i < len(image_matches) else ""
                        if isinstance(image_url, str) and image_url.startswith("//"):
                            image_url = "https:" + image_url
                        suppliers.append({
                            "name": store_names[i] if i < len(store_names) else f"Supplier {i+1}",
                            "platform": "aliexpress",
                            "unit_cost": price,
                            "shipping_cost": round(price * 0.15, 2),
                            "shipping_days": "10-20",
                            "rating": float(ratings[i]) if i < len(ratings) else 4.5,
                            "total_orders": int(orders[i]) if i < len(orders) else 0,
                            "image_url": image_url,
                        })
            except Exception as e:
                logger.warning(f"AliExpress supplier search failed for '{product_name}': {e}")

        return suppliers


class GoogleTrendsScanner:
    """Uses pytrends library for real Google Trends data.

    Strategy:
    1. pytrends related queries for product keywords
    2. Multiple product-specific seed keywords for broader coverage
    """

    async def scan_rising_terms(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scan Google Trends for rising product-related searches"""
        products = []

        try:
            from pytrends.request import TrendReq

            pytrends = TrendReq(hl='en-US', tz=300, retries=3, backoff_factor=1.5)

            # More product-specific seed keywords
            seed_keywords = [
                "buy online", "best gadget", "amazon finds", "must have product",
                "viral product", "trending item",
            ]
            if category:
                seed_keywords = [f"best {category}", f"buy {category} online"]

            for keyword in seed_keywords[:3]:
                try:
                    pytrends.build_payload([keyword], cat=0, timeframe='now 7-d', geo='US')
                    related = pytrends.related_queries()

                    if keyword in related and related[keyword].get("rising") is not None:
                        rising_df = related[keyword]["rising"]
                        for _, row in rising_df.head(8).iterrows():
                            query = row.get("query", "")
                            value = row.get("value", 0)

                            if query and len(query) > 3:
                                products.append({
                                    "source": "google_trends",
                                    "name": query.title(),
                                    "trend_data": {
                                        "search_term": query,
                                        "growth_percent": int(value) if value != "Breakout" else 5000,
                                        "monthly_volume": 0,
                                        "trend_direction": "up",
                                    },
                                    "discovered_at": datetime.now(timezone.utc).isoformat(),
                                })

                    # Also get top queries for more product ideas
                    if keyword in related and related[keyword].get("top") is not None:
                        top_df = related[keyword]["top"]
                        for _, row in top_df.head(5).iterrows():
                            query = row.get("query", "")
                            value = row.get("value", 0)
                            if query and len(query) > 3:
                                # Avoid duplicates
                                existing = {p["name"].lower() for p in products}
                                if query.title().lower() not in existing:
                                    products.append({
                                        "source": "google_trends",
                                        "name": query.title(),
                                        "trend_data": {
                                            "search_term": query,
                                            "growth_percent": int(value),
                                            "monthly_volume": 0,
                                            "trend_direction": "stable",
                                        },
                                        "discovered_at": datetime.now(timezone.utc).isoformat(),
                                    })

                    await asyncio.sleep(2)  # Rate limit pytrends more conservatively
                except Exception as e:
                    logger.warning(f"Google Trends failed for '{keyword}': {e}")

        except ImportError:
            logger.error("pytrends not installed - Google Trends scanner disabled")

        logger.info(f"Google Trends scanner found {len(products)} products")
        return products[:12]


class MetaAdLibraryScanner:
    """Scrapes the public Meta Ad Library for competitor ad data"""

    SEARCH_URL = "https://www.facebook.com/ads/library/"
    API_URL = "https://www.facebook.com/ads/library/async/search_ads/"

    async def scan_product_ads(self, product_name: str) -> Dict[str, Any]:
        """Scrape Meta Ad Library for ads related to a product"""
        result = {
            "product": product_name,
            "total_ads": 0,
            "active_ads": 0,
            "top_advertisers": [],
            "common_hooks": [],
            "avg_ad_duration_days": 0,
            "scanned_at": datetime.now(timezone.utc).isoformat(),
        }

        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            try:
                params = {
                    "active_status": "active",
                    "ad_type": "all",
                    "country": "US",
                    "q": product_name,
                    "media_type": "all",
                }
                resp = await client.get(
                    self.SEARCH_URL,
                    params=params,
                    headers=_get_headers(0),
                )

                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")

                    ad_cards = soup.select("._7jvw, .x1dr75xp, [data-testid='ad_library_card']")
                    result["total_ads"] = len(ad_cards)
                    result["active_ads"] = len(ad_cards)

                    advertisers = {}
                    for card in ad_cards[:20]:
                        name_el = card.select_one("._7jyr, .x8t9es0, a[href*='page_id']")
                        if name_el:
                            name = name_el.get_text(strip=True)
                            advertisers[name] = advertisers.get(name, 0) + 1

                    result["top_advertisers"] = [
                        {"name": name, "ad_count": count}
                        for name, count in sorted(advertisers.items(), key=lambda x: x[1], reverse=True)[:5]
                    ]

                    hooks = set()
                    for card in ad_cards[:10]:
                        text_el = card.select_one("._7jws, .x1iorvi4, div[data-testid='ad_creative_body']")
                        if text_el:
                            text = text_el.get_text(strip=True)
                            first_line = text.split(".")[0].strip()
                            if first_line and len(first_line) > 5:
                                hooks.add(first_line[:80])

                    result["common_hooks"] = list(hooks)[:5]

                    if result["total_ads"] == 0:
                        result = await self._search_via_api(client, product_name, result)

            except Exception as e:
                logger.warning(f"Meta Ad Library scrape failed for '{product_name}': {e}")

        return result

    async def _search_via_api(self, client: httpx.AsyncClient, product_name: str, result: Dict) -> Dict:
        """Try the Meta Ad Library API endpoint as fallback"""
        try:
            resp = await client.get(
                "https://www.facebook.com/ads/library/",
                params={
                    "active_status": "active",
                    "ad_type": "all",
                    "country": "ALL",
                    "q": product_name,
                },
                headers={**_get_headers(1), "Accept": "text/html"},
            )
            if resp.status_code == 200:
                text = resp.text
                count_match = re.search(r'(\d[\d,]*)\s*(?:results|ads)', text, re.I)
                if count_match:
                    count = int(count_match.group(1).replace(",", ""))
                    result["total_ads"] = count
                    result["active_ads"] = count
        except Exception as e:
            logger.warning(f"Meta Ad Library API fallback failed: {e}")
        return result


class CompetitorScanner:
    """Scrapes competitor Shopify stores via their public products.json"""

    async def scan_store(self, store_url: str) -> Dict[str, Any]:
        """Scrape a Shopify store's product catalog via products.json"""
        store_url = store_url.rstrip("/")
        if not store_url.startswith("http"):
            store_url = f"https://{store_url}"

        result = {
            "store_url": store_url,
            "store_name": store_url.split("//")[-1].split(".")[0].title(),
            "products": [],
            "total_products": 0,
            "new_products_count": 0,
            "scanned_at": datetime.now(timezone.utc).isoformat(),
        }

        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            try:
                products_url = f"{store_url}/products.json"
                resp = await client.get(products_url, headers=_get_headers(0))

                if resp.status_code == 200:
                    data = resp.json()
                    raw_products = data.get("products", [])

                    for p in raw_products:
                        variants = p.get("variants", [{}])
                        prices = [float(v.get("price", "0")) for v in variants if v.get("price")]
                        price = min(prices) if prices else 0

                        result["products"].append({
                            "name": p.get("title", "Unknown"),
                            "price": price,
                            "category": p.get("product_type", "Uncategorized"),
                            "url": f"{store_url}/products/{p.get('handle', '')}",
                            "image_url": (p.get("images", [{}])[0].get("src", "") if p.get("images") else ""),
                            "created_at": p.get("created_at", ""),
                            "updated_at": p.get("updated_at", ""),
                        })

                    result["total_products"] = len(result["products"])
                    result["store_name"] = _extract_store_name(resp.text, store_url)

                    page = 2
                    while len(raw_products) == 30 and page <= 5:
                        resp2 = await client.get(f"{products_url}?page={page}", headers=_get_headers(1))
                        if resp2.status_code == 200:
                            more = resp2.json().get("products", [])
                            if not more:
                                break
                            raw_products = more
                            for p in more:
                                variants = p.get("variants", [{}])
                                prices = [float(v.get("price", "0")) for v in variants if v.get("price")]
                                price = min(prices) if prices else 0
                                result["products"].append({
                                    "name": p.get("title", "Unknown"),
                                    "price": price,
                                    "category": p.get("product_type", "Uncategorized"),
                                    "url": f"{store_url}/products/{p.get('handle', '')}",
                                    "image_url": (p.get("images", [{}])[0].get("src", "") if p.get("images") else ""),
                                    "created_at": p.get("created_at", ""),
                                    "updated_at": p.get("updated_at", ""),
                                })
                            result["total_products"] = len(result["products"])
                            page += 1
                        else:
                            break
                        await asyncio.sleep(0.5)
                else:
                    logger.warning(f"Could not access {products_url} - status {resp.status_code}. Store may not be Shopify.")

            except Exception as e:
                logger.warning(f"Competitor store scrape failed for {store_url}: {e}")

        return result

    async def detect_new_products(self, store_url: str, previous_products: List[str]) -> List[Dict[str, Any]]:
        """Detect new products added to a store since last scan"""
        current_scan = await self.scan_store(store_url)
        previous_names = set(previous_products)

        new_products = [
            product for product in current_scan["products"]
            if product["name"] not in previous_names
        ]
        return new_products


class ProductScoutEngine:
    """Main engine that orchestrates all real scrapers"""

    def __init__(self):
        self.tiktok = TikTokScanner()
        self.amazon = AmazonScanner()
        self.aliexpress = AliExpressScanner()
        self.google_trends = GoogleTrendsScanner()
        self.meta_ads = MetaAdLibraryScanner()
        self.competitor = CompetitorScanner()

    async def run_full_scan(self) -> Dict[str, Any]:
        """Run a full scan across all real sources"""
        results = await asyncio.gather(
            self.tiktok.scan_trending(),
            self.amazon.scan_movers_shakers(),
            self.aliexpress.scan_trending(),
            self.google_trends.scan_rising_terms(),
            return_exceptions=True,
        )

        all_products = []
        source_stats = {}

        sources = ["tiktok", "amazon", "aliexpress", "google_trends"]
        for i, source in enumerate(sources):
            if isinstance(results[i], list):
                all_products.extend(results[i])
                source_stats[source] = len(results[i])
            else:
                logger.warning(f"Scanner {source} returned error: {results[i]}")
                source_stats[source] = 0

        logger.info(f"Full scan complete: {len(all_products)} total products | Stats: {source_stats}")
        return {
            "total_products": len(all_products),
            "products": all_products,
            "source_stats": source_stats,
            "scan_time": datetime.now(timezone.utc).isoformat(),
        }

    async def analyze_product(self, product_name: str) -> Dict[str, Any]:
        """Analyze a specific product across sources"""
        ad_data = await self.meta_ads.scan_product_ads(product_name)
        suppliers = await self.aliexpress.find_suppliers(product_name)

        return {
            "product_name": product_name,
            "competition_analysis": ad_data,
            "suppliers": suppliers,
            "recommendation": "low_competition" if ad_data["total_ads"] < 50 else "high_competition",
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }


# ========== Helper Functions ==========

def _parse_price(text: str) -> float:
    """Extract price from text like '$29.99' or 'US $5.80'"""
    match = re.search(r'[\d,]+\.?\d*', text.replace(",", ""))
    return float(match.group()) if match else 0.0


def _parse_order_count(text: str) -> int:
    """Parse order count from text like '1.2K+ sold' or '15,000 orders'"""
    text = text.lower().replace(",", "").replace("+", "")
    match = re.search(r'([\d.]+)\s*k', text)
    if match:
        return int(float(match.group(1)) * 1000)
    match = re.search(r'(\d+)', text)
    return int(match.group(1)) if match else 0


def _parse_view_count(text: str) -> int:
    """Parse view count from text like '47.2M views' or '1.5B views'"""
    text = text.upper().replace(",", "")
    match = re.search(r'([\d.]+)\s*B', text)
    if match:
        return int(float(match.group(1)) * 1_000_000_000)
    match = re.search(r'([\d.]+)\s*M', text)
    if match:
        return int(float(match.group(1)) * 1_000_000)
    match = re.search(r'([\d.]+)\s*K', text)
    if match:
        return int(float(match.group(1)) * 1_000)
    match = re.search(r'(\d+)', text)
    return int(match.group(1)) if match else 0


def _extract_product_name(description: str, hashtag: str) -> str:
    """Best-effort extraction of a product name from a TikTok video description"""
    cleaned = re.sub(r'#\w+', '', description)
    cleaned = re.sub(r'[^\w\s\-\']', '', cleaned).strip()
    words = cleaned.split()
    if len(words) > 2:
        return " ".join(words[:5]).title()
    return hashtag.replace("_", " ").title()


def _extract_store_name(html: str, url: str) -> str:
    """Extract store name from page HTML or fall back to URL"""
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find("title")
    if title:
        name = title.get_text(strip=True).split("|")[0].split("-")[0].strip()
        if name and len(name) > 1:
            return name
    return url.split("//")[-1].split(".")[0].title()
