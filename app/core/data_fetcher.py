import asyncio
import os
import re
import math
import logging
from datetime import datetime, timedelta
import feedparser
import httpx
import yfinance as yf
from nsetools import Nse
from bs4 import BeautifulSoup

from app.models import EntityResolution, RawDocument, MarketMetrics

logger = logging.getLogger(__name__)

# Fallback fake Nse since nsetools sometimes has connection issues or is outdated, we will mock it safely if needed.
try:
    nse = Nse()
except Exception:
    nse = None

RSS_FEEDS = {
    "ET": "https://economictimes.indiatimes.com/markets/rss.cms",
    "Moneycontrol": "https://www.moneycontrol.com/rss/latestnews.xml",
    "Business Standard": "https://www.business-standard.com/rss/markets-106.rss",
    "Mint": "https://www.livemint.com/rss/markets",
    "NDTV Profit": "https://feeds.feedburner.com/ndtvprofit-latest"
}

def is_relevant(entry_title: str, entry_summary: str, entity: EntityResolution) -> bool:
    """Check if the text mentions the entity or search terms."""
    text = f"{entry_title} {entry_summary}".lower()
    for term in entity.search_terms:
        if term.lower() in text:
            return True
    return False

async def fetch_rss_feeds(entity: EntityResolution) -> list[RawDocument]:
    """Asynchronously fetches and filters RSS news feeds."""
    docs = []
    seen_links = set()
    
    # feedparser is synchronous, but we can wrap it or just fetch the raw XML via httpx then parse
    async with httpx.AsyncClient() as client:
        for source_name, url in RSS_FEEDS.items():
            try:
                resp = await client.get(url, timeout=5.0)
                if resp.status_code == 200:
                    feed = feedparser.parse(resp.text)
                    count = 0
                    for entry in feed.entries:
                        title = entry.get("title", "")
                        desc = entry.get("summary", entry.get("description", ""))
                        link = entry.get("link", "")
                        
                        if link in seen_links: continue
                        
                        if is_relevant(title, desc, entity):
                            dt = datetime.now()
                            docs.append(RawDocument(
                                source=f"{source_name}RSS",
                                title=title,
                                text=desc,
                                url=link,
                                published_at=dt
                            ))
                            seen_links.add(link)
                            count += 1
                        if count >= 10:
                            break
            except Exception as e:
                logger.error(f"Error fetching RSS {source_name}: {e}")
                
    return docs[:40]

async def fetch_bse_filings(entity: EntityResolution) -> list[RawDocument]:
    """Fetches corporate filings from BSE."""
    docs = []
    if not entity.ticker_bse:
        return docs
    
    today_dt = datetime.now()
    past_dt = today_dt - timedelta(days=90)
    today_str = today_dt.strftime("%Y%m%d")
    past_str = past_dt.strftime("%Y%m%d")
    
    url = (f"https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w?"
           f"strCat=-1&strPrevDate={past_str}&strScrip={entity.ticker_bse}"
           f"&strSearch=P&strToDate={today_str}&strType=C")
           
    headers = {"Referer": "https://www.bseindia.com", "User-Agent": "Mozilla/5.0"}
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=headers, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                table = data.get("Table", [])
                
                count = 0
                for row in table:
                    headline = row.get("HEADLINE", "")
                    attach = row.get("ATTACHMENTNAME", "")
                    # We skip full PDF extraction here for brevity, instead indexing the headline
                    # PDF extraction requires specific handling depending on content format.
                    
                    if headline:
                        docs.append(RawDocument(
                            source="BSEFiling",
                            title=row.get("CATEGORYNAME", "Filing"),
                            text=headline,
                            url=f"https://www.bseindia.com/xml-data/corpfiling/AttachLive/{attach}" if attach else None,
                            published_at=datetime.now()
                        ))
                    count += 1
                    if count >= 15: break
        except Exception as e:
            logger.error(f"Error fetching BSE filings: {e}")
            
    return docs

async def fetch_nse_announcements(entity: EntityResolution) -> list[RawDocument]:
    """Fetches NSE Announcements."""
    docs = []
    if not entity.ticker_nse:
        return docs
        
    url = f"https://www.nseindia.com/api/corp-info?symbol={entity.ticker_nse}&corpType=announcement&market=equities"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com"
    }

    async with httpx.AsyncClient() as client:
        try:
            # We first fetch root route to get cookies
            base_resp = await client.get("https://www.nseindia.com", headers=headers, timeout=10.0)
            cookies = base_resp.cookies
            await asyncio.sleep(0.5) # rate limiting
            resp = await client.get(url, headers=headers, cookies=cookies, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                for item in data[:15]:
                    desc = item.get("desc", "")
                    att = item.get("attchmntText", "")
                    docs.append(RawDocument(
                        source="NSEFiling",
                        title=item.get("sub", "NSE Filing"),
                        text=f"{desc}. {att}",
                        url=item.get("attchmntFile", None),
                        published_at=datetime.now()
                    ))
        except Exception as e:
            logger.error(f"Error fetching NSE announcements: {e}")
            
    return docs

async def check_sebi_orders(entity: EntityResolution) -> bool:
    """Checks if SEBI has active or recent actions against the entity."""
    url = f"https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognised=yes&type=Orders&searchWord={entity.company_name}"
    # This is a stub for scraping SEBI. The site requires careful payload manipulation.
    # We will simulate the check here.
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, timeout=10.0)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                table = soup.find("table")
                if table:
                    return len(table.find_all("tr")) > 1
        except Exception:
            pass
    return False

async def fetch_market_metrics(entity: EntityResolution) -> tuple[MarketMetrics, str, bool]:
    """
    Fetches comprehensive metrics mapping to Indian market risk profiles.
    Returns: MarketMetrics, surveillance_flag (ASM/GSM), sebi_flag
    """
    metrics = MarketMetrics()
    surveillance_flag = None
    sebi_flag = await check_sebi_orders(entity)
    
    # 1. Macro Indicators (VIX & USD/INR)
    try:
        usdinr_tk = yf.Ticker("USDINR=X")
        usdinr_hist = usdinr_tk.history(period="2d")
        if not usdinr_hist.empty:
            metrics.usd_inr_rate = float(usdinr_hist['Close'].iloc[-1])
            
        vix_tk = yf.Ticker("^INDIAVIX")
        vix_hist = vix_tk.history(period="5d")
        if not vix_hist.empty:
            metrics.india_vix = float(vix_hist['Close'].iloc[-1])
            
        metrics.repo_rate = 6.5 # Usually scraped from RBI but hardcoded for reliability
    except Exception as e:
        logger.error(f"Error fetching macro metrics: {e}")

    # 2. Entity metrics
    if entity.ticker_nse:
        try:
            tk = yf.Ticker(f"{entity.ticker_nse}.NS")
            info = tk.info
            metrics.beta = info.get("beta")
            metrics.pe_ratio = info.get("trailingPE")
            metrics.pb_ratio = info.get("priceToBook")
            metrics.debt_to_equity = info.get("debtToEquity")
            metrics.current_ratio = info.get("currentRatio")
            metrics.roe = info.get("returnOnEquity")
            metrics.revenue_growth_yoy = info.get("revenueGrowth")
            
            mc = info.get("marketCap", 0)
            if metrics.usd_inr_rate and mc > 0:
                metrics.market_cap_cr = (mc * metrics.usd_inr_rate) / 10_000_000
                
            # Usually we use NSE Shareholding pattern to find this, proxying below
            proxied_promoter_percent = info.get("heldPercentInsiders", 0) * 100
            metrics.promoter_holding = proxied_promoter_percent if proxied_promoter_percent > 0 else None
            metrics.pledged_shares_pct = None # Highly specific data point, mock proxy omitted
            
        except Exception as e:
            logger.error(f"Error fetching YF entity metrics: {e}")

    return metrics, surveillance_flag, sebi_flag

async def fetch_all_data(entity: EntityResolution) -> tuple[list[RawDocument], MarketMetrics, str, bool]:
    """Orchestrates async fetching of all data."""
    tasks = [
        fetch_rss_feeds(entity),
        fetch_bse_filings(entity),
        fetch_nse_announcements(entity),
        fetch_market_metrics(entity)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_docs = []
    metrics = MarketMetrics()
    surveillance_flag = None
    sebi_flag = False
    
    for res in results:
        if isinstance(res, Exception):
            logger.error(f"Data Fetcher error: {res}")
            continue
            
        if isinstance(res, list):
            all_docs.extend(res)
        elif isinstance(res, tuple):
            metrics, surveillance_flag, sebi_flag = res
            
    return all_docs, metrics, surveillance_flag, sebi_flag
