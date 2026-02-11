"""
Product Scout Services - Real Web Scrapers
Scrapes Amazon, AliExpress, TikTok Creative Center, Meta Ad Library, and Google Trends
using httpx + BeautifulSoup for lightweight HTTP-based scraping.
"""
import asyncio
import logging
import re
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus, urlencode

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Rotating user agents to avoid blocks
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]

def _get_headers(idx: int = 0) -> Dict[str, str]:
    ua = USER_AGENTS[idx % len(USER_AGENTS)]
    return {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }


class TikTokScanner:
    """Scrapes TikTok Creative Center for trending products and hashtags"""

    CREATIVE_CENTER_URL = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en"
    # TikTok Creative Center has internal API endpoints
    HASHTAG_API = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list"

    async def scan_trending(self, niche: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scan TikTok Creative Center for trending hashtags related to products"""
        products = []
        product_hashtags = [
            "tiktokmademebuyit", "amazonfinds", "viralproducts",
            "musthave", "gadgettok", "homeessentials", "cleaningtok",
        ]

        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            # Try Creative Center API for trending hashtags
            try:
                resp = await client.get(
                    self.HASHTAG_API,
                    params={
                        "page": 1,
                        "limit": 50,
                        "period": 7,
                        "country_code": "US",
                        "sort_by": "popular",
                    },
                    headers={
                        **_get_headers(0),
                        "Referer": self.CREATIVE_CENTER_URL,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    # Broader keyword matching for product-related hashtags
                    product_kw = [
                        "buy", "find", "product", "gadget", "must", "hack", "deal",
                        "clean", "home", "kitchen", "beauty", "fitness", "tech", "gift",
                        "amazon", "shop", "unbox", "review", "haul", "worth", "best",
                        "tool", "organiz", "storage", "lamp", "light", "phone", "car",
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
            except Exception as e:
                logger.warning(f"TikTok Creative Center API failed: {e}")

            # Fallback: scrape TikTok tag pages
            if not products:
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

                            # Also try __UNIVERSAL_DATA_FOR_REHYDRATION__ for video descriptions
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

        logger.info(f"TikTok scanner found {len(products)} products")
        return products[:10]


class AmazonScanner:
    """Scrapes Amazon Movers & Shakers for trending products"""

    MOVERS_URLS = {
        "Electronics": "https://www.amazon.com/gp/movers-and-shakers/electronics",
        "Home & Kitchen": "https://www.amazon.com/gp/movers-and-shakers/home-garden",
        "Beauty": "https://www.amazon.com/gp/movers-and-shakers/beauty",
        "Sports & Outdoors": "https://www.amazon.com/gp/movers-and-shakers/sporting-goods",
        "Health & Personal Care": "https://www.amazon.com/gp/movers-and-shakers/hpc",
        "Pet Supplies": "https://www.amazon.com/gp/movers-and-shakers/pet-supplies",
    }

    async def scan_movers_shakers(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scrape Amazon Movers & Shakers for products with biggest rank increases"""
        products = []
        urls = {}

        if category and category in self.MOVERS_URLS:
            urls = {category: self.MOVERS_URLS[category]}
        else:
            for cat in ["Electronics", "Home & Kitchen", "Beauty"]:
                urls[cat] = self.MOVERS_URLS[cat]

        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            for cat_name, url in urls.items():
                try:
                    resp = await client.get(url, headers=_get_headers(2))
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, "html.parser")

                        # Try multiple selector strategies - Amazon frequently changes class names
                        items = soup.select("#zg-ordered-list li, .zg-item-immersion")

                        # Fallback: look for any div/li with product links
                        if not items:
                            items = soup.select("div[data-asin], div[id*='gridItem']")

                        # Fallback: broader approach - find all links to /dp/ product pages
                        if not items:
                            links = soup.select("a[href*='/dp/']")
                            seen_names = set()
                            for link in links[:15]:
                                name = link.get_text(strip=True)
                                if name and len(name) > 5 and len(name) < 200 and name not in seen_names:
                                    seen_names.add(name)
                                    # Find nearby image
                                    parent = link.find_parent("div")
                                    img_el = parent.select_one("img[src]") if parent else None
                                    image_url = img_el.get("src", "") if img_el else ""
                                    # Find nearby price
                                    price = 0
                                    price_el = parent.select_one(".a-price .a-offscreen, span.a-price span") if parent else None
                                    if price_el:
                                        price = _parse_price(price_el.get_text(strip=True))

                                    products.append({
                                        "source": "amazon",
                                        "name": name[:80],
                                        "image_url": image_url,
                                        "trend_data": {
                                            "rank_change": 0,
                                            "category": cat_name,
                                            "current_price": price,
                                        },
                                        "discovered_at": datetime.now(timezone.utc).isoformat(),
                                    })
                            if products:
                                logger.info(f"Amazon: fallback link parsing found {len(products)} for {cat_name}")

                        for item in items[:5]:
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

                            price_text = price_el.get_text(strip=True) if price_el else "$0"
                            price = _parse_price(price_text)
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
                                "name": name[:80],
                                "image_url": image_url,
                                "trend_data": {
                                    "rank_change": rank_change,
                                    "category": cat_name,
                                    "current_price": price,
                                },
                                "discovered_at": datetime.now(timezone.utc).isoformat(),
                            })

                    await asyncio.sleep(1)
                except Exception as e:
                    logger.warning(f"Amazon scrape failed for {cat_name}: {e}")

        logger.info(f"Amazon scanner found {len(products)} products")
        return products[:15]


class AliExpressScanner:
    """Scrapes AliExpress for trending/hot products with supplier data"""

    SEARCH_URL = "https://www.aliexpress.com/w/wholesale-{query}.html"
    HOT_URL = "https://www.aliexpress.com/popular/{category}.html"

    async def scan_trending(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scrape AliExpress for hot products with supplier pricing"""
        products = []
        search_terms = [
            "trending gadgets 2026", "viral tiktok products",
            "dropshipping hot products", "new arrivals bestseller",
        ]
        if category:
            search_terms = [f"{category} bestseller", f"{category} trending"]

        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            for term in search_terms[:2]:
                try:
                    url = f"https://www.aliexpress.com/w/wholesale-{quote_plus(term)}.html"
                    params = {"SortType": "total_tranpro_desc"}  # Sort by orders
                    resp = await client.get(url, params=params, headers=_get_headers(3))

                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, "html.parser")

                        # AliExpress renders product data in script tags
                        for script in soup.find_all("script"):
                            text = script.string or ""
                            if "window._dida_config_" in text or "runParams" in text:
                                # Extract product JSON data
                                json_matches = re.findall(r'"title":"([^"]{5,80})"', text)
                                price_matches = re.findall(r'"minPrice":"?(\d+\.?\d*)"?', text)
                                order_matches = re.findall(r'"tradeCount":"?(\d+)"?', text)
                                rating_matches = re.findall(r'"starRating":"?(\d+\.?\d*)"?', text)
                                image_matches = re.findall(r'"imgUrl":"(https?://[^"]+)"', text)

                                for i in range(min(len(json_matches), 8)):
                                    name = json_matches[i]
                                    price = float(price_matches[i]) if i < len(price_matches) else 0
                                    orders = int(order_matches[i]) if i < len(order_matches) else 0
                                    rating = float(rating_matches[i]) if i < len(rating_matches) else 0
                                    image_url = image_matches[i] if i < len(image_matches) else ""

                                    if price > 0 and name:
                                        products.append({
                                            "source": "aliexpress",
                                            "name": name,
                                            "image_url": image_url,
                                            "trend_data": {
                                                "orders_30d": orders,
                                                "price": price,
                                                "rating": rating,
                                                "order_velocity": round(orders / 30, 1) if orders else 0,
                                            },
                                            "discovered_at": datetime.now(timezone.utc).isoformat(),
                                        })

                        # Alternative: parse product cards directly
                        if not products:
                            cards = soup.select(".list--gallery--C2f2tvm .multi--container--1UZxxHY, .search-card-item")
                            for card in cards[:8]:
                                title_el = card.select_one(".multi--titleText--nXeOvyr, h3")
                                price_el = card.select_one(".multi--price-sale--U-S0jtj, .search-card-e-price-main")
                                orders_el = card.select_one(".multi--trade--Ktbl2jB, .search-card-e-review")
                                img_el = card.select_one("img[src]")

                                title = title_el.get_text(strip=True) if title_el else None
                                if not title:
                                    continue

                                price = _parse_price(price_el.get_text(strip=True)) if price_el else 0
                                orders_text = orders_el.get_text(strip=True) if orders_el else "0"
                                orders = _parse_order_count(orders_text)
                                image_url = img_el.get("src", "") if img_el else ""

                                products.append({
                                    "source": "aliexpress",
                                    "name": title[:80],
                                    "image_url": image_url,
                                    "trend_data": {
                                        "orders_30d": orders,
                                        "price": price,
                                        "rating": 0,
                                        "order_velocity": round(orders / 30, 1) if orders else 0,
                                    },
                                    "discovered_at": datetime.now(timezone.utc).isoformat(),
                                })

                    await asyncio.sleep(1)
                except Exception as e:
                    logger.warning(f"AliExpress scrape failed for '{term}': {e}")

        logger.info(f"AliExpress scanner found {len(products)} products")
        return products[:15]

    async def find_suppliers(self, product_name: str) -> List[Dict[str, Any]]:
        """Find suppliers for a specific product on AliExpress"""
        suppliers = []

        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            try:
                url = f"https://www.aliexpress.com/w/wholesale-{quote_plus(product_name)}.html"
                params = {"SortType": "total_tranpro_desc"}
                resp = await client.get(url, params=params, headers=_get_headers(4))

                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")

                    # Parse product listings as potential suppliers
                    for script in soup.find_all("script"):
                        text = script.string or ""
                        if "window._dida_config_" in text or "runParams" in text:
                            titles = re.findall(r'"title":"([^"]{5,80})"', text)
                            prices = re.findall(r'"minPrice":"?(\d+\.?\d*)"?', text)
                            orders = re.findall(r'"tradeCount":"?(\d+)"?', text)
                            ratings = re.findall(r'"starRating":"?(\d+\.?\d*)"?', text)
                            store_names = re.findall(r'"storeName":"([^"]+)"', text)

                            for i in range(min(len(titles), 5)):
                                price = float(prices[i]) if i < len(prices) else 0
                                if price <= 0:
                                    continue
                                suppliers.append({
                                    "name": store_names[i] if i < len(store_names) else f"Supplier {i+1}",
                                    "platform": "aliexpress",
                                    "unit_cost": price,
                                    "shipping_cost": round(price * 0.15, 2),  # Estimate ~15% for ePacket
                                    "shipping_days": "10-20",
                                    "rating": float(ratings[i]) if i < len(ratings) else 4.5,
                                    "total_orders": int(orders[i]) if i < len(orders) else 0,
                                })
            except Exception as e:
                logger.warning(f"AliExpress supplier search failed for '{product_name}': {e}")

        return suppliers


class GoogleTrendsScanner:
    """Uses pytrends library for real Google Trends data"""

    async def scan_rising_terms(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scan Google Trends for rising product-related searches"""
        products = []

        try:
            from pytrends.request import TrendReq

            pytrends = TrendReq(hl='en-US', tz=300)

            # Product-related seed keywords to find rising terms
            seed_keywords = [
                "buy", "gadget", "product", "Amazon find",
            ]
            if category:
                seed_keywords = [category]

            for keyword in seed_keywords[:2]:
                try:
                    pytrends.build_payload([keyword], cat=0, timeframe='now 7-d', geo='US')
                    related = pytrends.related_queries()

                    if keyword in related and related[keyword].get("rising") is not None:
                        rising_df = related[keyword]["rising"]
                        for _, row in rising_df.head(5).iterrows():
                            query = row.get("query", "")
                            value = row.get("value", 0)

                            # Filter for product-like terms (exclude people, places)
                            if query and len(query) > 3:
                                products.append({
                                    "source": "google_trends",
                                    "name": query.title(),
                                    "trend_data": {
                                        "search_term": query,
                                        "growth_percent": int(value) if value != "Breakout" else 5000,
                                        "monthly_volume": 0,  # pytrends doesn't give exact volume
                                        "trend_direction": "up",
                                    },
                                    "discovered_at": datetime.now(timezone.utc).isoformat(),
                                })

                    await asyncio.sleep(1)  # Rate limit pytrends
                except Exception as e:
                    logger.warning(f"Google Trends failed for '{keyword}': {e}")

        except ImportError:
            logger.error("pytrends not installed - Google Trends scanner disabled")

        logger.info(f"Google Trends scanner found {len(products)} products")
        return products[:10]


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
                # Search the public ad library page
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

                    # Count ad results
                    ad_cards = soup.select("._7jvw, .x1dr75xp, [data-testid='ad_library_card']")
                    result["total_ads"] = len(ad_cards)
                    result["active_ads"] = len(ad_cards)

                    # Extract advertiser names
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

                    # Extract common hooks from ad text
                    hooks = set()
                    for card in ad_cards[:10]:
                        text_el = card.select_one("._7jws, .x1iorvi4, div[data-testid='ad_creative_body']")
                        if text_el:
                            text = text_el.get_text(strip=True)
                            # First line is usually the hook
                            first_line = text.split(".")[0].strip()
                            if first_line and len(first_line) > 5:
                                hooks.add(first_line[:80])

                    result["common_hooks"] = list(hooks)[:5]

                    # If we got no results from HTML, try the async endpoint
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
                # Count approximate results from page text
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
        # Normalize URL
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
                # Shopify stores expose products.json publicly
                products_url = f"{store_url}/products.json"
                resp = await client.get(products_url, headers=_get_headers(0))

                if resp.status_code == 200:
                    data = resp.json()
                    raw_products = data.get("products", [])

                    for p in raw_products:
                        # Get the lowest variant price
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

                    # Paginate if more products (Shopify returns 30 per page)
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
    # Remove hashtags and emojis, take first meaningful phrase
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
