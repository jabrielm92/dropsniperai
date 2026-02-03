"""Google Trends integration using pytrends"""
from fastapi import APIRouter, Depends, HTTPException
from pytrends.request import TrendReq
import asyncio
from typing import List, Optional
from datetime import datetime, timezone

from models import User
from routes.deps import get_db, get_current_user

router = APIRouter(prefix="/trends", tags=["trends"])

def get_pytrends():
    """Create pytrends instance"""
    return TrendReq(hl='en-US', tz=360)

@router.get("/rising")
async def get_rising_trends(
    category: Optional[str] = None,
    geo: str = "US",
    user: User = Depends(get_current_user)
):
    """Get rising search trends from Google Trends"""
    try:
        pytrends = get_pytrends()
        
        # Get trending searches
        trending = await asyncio.to_thread(
            pytrends.trending_searches,
            pn=geo.lower()
        )
        
        trends_list = trending[0].tolist()[:20] if not trending.empty else []
        
        return {
            "source": "google_trends",
            "geo": geo,
            "trending_searches": trends_list,
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "source": "google_trends",
            "error": str(e),
            "trending_searches": [],
            "fallback": True
        }

@router.get("/interest/{keyword}")
async def get_keyword_interest(
    keyword: str,
    timeframe: str = "today 3-m",
    geo: str = "US",
    user: User = Depends(get_current_user)
):
    """Get interest over time for a specific keyword"""
    try:
        pytrends = get_pytrends()
        
        await asyncio.to_thread(
            pytrends.build_payload,
            [keyword],
            timeframe=timeframe,
            geo=geo
        )
        
        interest = await asyncio.to_thread(pytrends.interest_over_time)
        
        if interest.empty:
            return {"keyword": keyword, "data": [], "average": 0}
        
        data = []
        for date, row in interest.iterrows():
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "interest": int(row[keyword])
            })
        
        avg_interest = sum(d["interest"] for d in data) / len(data) if data else 0
        
        # Determine trend direction
        if len(data) >= 4:
            first_quarter = sum(d["interest"] for d in data[:len(data)//4]) / (len(data)//4)
            last_quarter = sum(d["interest"] for d in data[-len(data)//4:]) / (len(data)//4)
            if last_quarter > first_quarter * 1.1:
                trend = "up"
            elif last_quarter < first_quarter * 0.9:
                trend = "down"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return {
            "keyword": keyword,
            "data": data,
            "average": round(avg_interest, 1),
            "trend_direction": trend,
            "geo": geo,
            "timeframe": timeframe
        }
    except Exception as e:
        return {
            "keyword": keyword,
            "error": str(e),
            "data": [],
            "fallback": True
        }

@router.get("/related/{keyword}")
async def get_related_queries(
    keyword: str,
    geo: str = "US",
    user: User = Depends(get_current_user)
):
    """Get related queries for a keyword"""
    try:
        pytrends = get_pytrends()
        
        await asyncio.to_thread(
            pytrends.build_payload,
            [keyword],
            timeframe="today 3-m",
            geo=geo
        )
        
        related = await asyncio.to_thread(pytrends.related_queries)
        
        result = {
            "keyword": keyword,
            "rising": [],
            "top": []
        }
        
        if keyword in related:
            if related[keyword]['rising'] is not None:
                rising_df = related[keyword]['rising']
                result["rising"] = [
                    {"query": row['query'], "value": int(row['value']) if row['value'] != 'Breakout' else 1000}
                    for _, row in rising_df.head(10).iterrows()
                ]
            
            if related[keyword]['top'] is not None:
                top_df = related[keyword]['top']
                result["top"] = [
                    {"query": row['query'], "value": int(row['value'])}
                    for _, row in top_df.head(10).iterrows()
                ]
        
        return result
    except Exception as e:
        return {
            "keyword": keyword,
            "error": str(e),
            "rising": [],
            "top": [],
            "fallback": True
        }

@router.post("/analyze-products")
async def analyze_products_trends(
    product_names: List[str],
    geo: str = "US",
    user: User = Depends(get_current_user)
):
    """Analyze Google Trends for multiple product names"""
    db = get_db()
    results = []
    
    for name in product_names[:5]:  # Limit to 5 to avoid rate limiting
        try:
            pytrends = get_pytrends()
            
            await asyncio.to_thread(
                pytrends.build_payload,
                [name],
                timeframe="today 3-m",
                geo=geo
            )
            
            interest = await asyncio.to_thread(pytrends.interest_over_time)
            
            if not interest.empty:
                values = interest[name].tolist()
                avg = sum(values) / len(values) if values else 0
                current = values[-1] if values else 0
                
                # Calculate trend
                if len(values) >= 4:
                    first_q = sum(values[:len(values)//4]) / (len(values)//4)
                    last_q = sum(values[-len(values)//4:]) / (len(values)//4)
                    change = ((last_q - first_q) / first_q * 100) if first_q > 0 else 0
                else:
                    change = 0
                
                results.append({
                    "product": name,
                    "current_interest": current,
                    "average_interest": round(avg, 1),
                    "change_percent": round(change, 1),
                    "trend": "up" if change > 10 else ("down" if change < -10 else "stable")
                })
            else:
                results.append({
                    "product": name,
                    "current_interest": 0,
                    "average_interest": 0,
                    "change_percent": 0,
                    "trend": "unknown"
                })
                
            await asyncio.sleep(1)  # Rate limiting
            
        except Exception as e:
            results.append({
                "product": name,
                "error": str(e),
                "trend": "error"
            })
    
    return {"results": results, "geo": geo}
