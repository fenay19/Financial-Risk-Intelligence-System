import asyncio
from datetime import datetime
import yfinance as yf
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.models import AnalyzeRequest, RiskReport, RiskSentence, CategoryRisk
from app.core.input_handler import resolve_entity, TICKER_MAP, SECTOR_MAP
from app.core.data_fetcher import fetch_all_data
from app.core.preprocessor import tokenize_and_stem
from app.core.tfidf_engine import TFIDFEngine
from app.core.sentiment import score_sentiment
from app.core.risk_scorer import calculate_overall_risk, get_risk_label
from app.core.cache import get_cached_report, save_to_cache, get_deltas

router = APIRouter()
tfidf_engine = TFIDFEngine()

@router.post("/api/analyze", response_model=RiskReport)
async def analyze_query(request: AnalyzeRequest):
    """Primary pipeline resolving entity, fetching data, extracting dimensions and scoring."""
    if not request.refresh:
        cached = get_cached_report(request.q)
        if cached:
            return RiskReport(**cached)
            
    entity = await resolve_entity(request.q)
    docs, metrics, surveillance_flag, sebi_flag = await fetch_all_data(entity)
    
    docs_text = [d.text for d in docs if d.text]
    top_terms = tfidf_engine.extract_top_terms(docs_text)
    
    risk_sentences = []
    
    for doc in docs:
        if not doc.text: continue
        sentences = [s.strip() for s in doc.text.split(".") if len(s.split()) > 4]
        for s in sentences:
            cat, sim, triggers = tfidf_engine.classify_sentence(s)
            sent = score_sentiment(s) # -1 to 1, where lower is worse contextually. Wait, our score_sentiment is positive - negative / total so negative implies worse.
            
            # Convert to aggressive risk score if mapped to category and negative sentiment
            # or if it mentions specific triggers.
            sentence_risk = 0.0
            if cat != "NONE" and sent < 0:
                sentence_risk = min(abs(sent) * sim * 100 * 2, 10.0) # bounded 0-10
            elif triggers:
                sentence_risk = 5.0
                
            if sentence_risk > 3.0:
                risk_sentences.append(RiskSentence(
                    text=s,
                    source=doc.source,
                    published_at=doc.published_at.isoformat() if doc.published_at else None,
                    category=cat,
                    risk_score=sentence_risk
                ))
                
    # Sort sentences to get top critical
    risk_sentences.sort(key=lambda x: x.risk_score, reverse=True)
    top_risk_sentences = risk_sentences[:5]
    
    final_score, cat_breakdown = calculate_overall_risk(risk_sentences, metrics, surveillance_flag, sebi_flag)
    
    report = RiskReport(
        query=request.q,
        entity=entity,
        risk_score=final_score,
        risk_label=get_risk_label(final_score),
        risk_delta=get_deltas(request.q),
        category_breakdown=cat_breakdown,
        top_sentences=top_risk_sentences,
        top_risk_terms=top_terms,
        market_metrics=metrics,
        documents_analyzed=len(docs),
        analysis_timestamp=datetime.now()
    )
    
    save_to_cache(
        request.q, 
        report.model_dump(mode='json'), 
        final_score, 
        metrics.india_vix or 0.0, 
        metrics.usd_inr_rate or 0.0
    )
    
    return report

@router.get("/api/market-pulse")
async def get_market_pulse():
    """Live snapshot of overarching Indian Market variables."""
    try:
        nifty = yf.Ticker("^NSEI").history(period="2d")
        sensex = yf.Ticker("^BSESN").history(period="2d")
        vix = yf.Ticker("^INDIAVIX").history(period="1d")
        usdinr = yf.Ticker("USDINR=X").history(period="1d")
        
        nifty_change = ((nifty['Close'].iloc[-1] - nifty['Close'].iloc[0]) / nifty['Close'].iloc[0]) * 100 if not nifty.empty else 0
        sensex_change = ((sensex['Close'].iloc[-1] - sensex['Close'].iloc[0]) / sensex['Close'].iloc[0]) * 100 if not sensex.empty else 0
        india_vix = vix['Close'].iloc[-1] if not vix.empty else 15.0
        usdinr_val = usdinr['Close'].iloc[-1] if not usdinr.empty else 83.0
        
        sentiment = "Neutral"
        if india_vix > 20: sentiment = "Cautious"
        if india_vix > 30: sentiment = "Fearful"
        if india_vix < 13: sentiment = "Optimistic"
        
        return {
            "india_vix": round(float(india_vix), 2),
            "usd_inr": round(float(usdinr_val), 2),
            "nifty50_pct_change": round(float(nifty_change), 2),
            "sensex_pct_change": round(float(sensex_change), 2),
            "repo_rate": 6.5,
            "market_sentiment": sentiment
        }
    except Exception as e:
        return {"error": str(e), "india_vix": 15.0, "usd_inr": 83.0, "market_sentiment": "Cautious (Fallback)"}

@router.get("/api/sector-risk/{sector_name}")
async def get_sector_risk(sector_name: str):
    """Orchestrates analysis across major constituents of an Indian sector."""
    normalized = sector_name.lower().strip()
    if normalized not in SECTOR_MAP:
        raise HTTPException(status_code=404, detail="Sector not mapped in our Indian framework.")
        
    stocks = SECTOR_MAP[normalized]["key_stocks"]
    results = []
    
    # In a full production, gather concurrently. Iterating sequentially for safety here.
    for stock in stocks:
        req = AnalyzeRequest(q=stock)
        rep = await analyze_query(req)
        results.append({
            "ticker": stock,
            "score": rep.risk_score,
            "label": rep.risk_label
        })
        
    avg_score = sum(r["score"] for r in results) / len(results)
    return {
        "sector": sector_name.capitalize(),
        "aggregate_score": round(avg_score, 2),
        "label": get_risk_label(avg_score),
        "constituents": results
    }

@router.get("/api/nifty-heatmap")
async def get_nifty_heatmap():
    """Generates a structured component payload for visualizing current known NIFTY 50 risks."""
    # We will pick a hardcoded highly relevant cross-section of available NIFTY 50 map keys
    # to synthesize a heatmap array mapping.
    
    targets = [
        "reliance", "tcs", "hdfcbank", "infy", "icicibank", "bajfinance", "wipro",
        "hul", "itc", "lnt", "sunpharma", "adanient", "ongc", "sbi", "maruti", 
        "tatamotors", "axisbank", "kotak", "dmart", "zomato"
    ]
    
    heat_tiles = []
    for t in targets:
        # Check cache explicitly first
        cached = get_cached_report(t)
        if cached:
            heat_tiles.append({
                "ticker": cached["entity"]["ticker_nse"],
                "score": cached["risk_score"]
            })
        else:
            # Provide base naive fallback for missing initial payloads or we can compute on the fly
            # Usually we don't compute whole NIFTY 50 on the fly per GET request.
            meta = TICKER_MAP.get(t)
            heat_tiles.append({
                "ticker": meta["nse"] if meta else t.upper(),
                "score": 0.0 # Will render neutrally requiring explicit fetch
            })
            
    heat_tiles.sort(key=lambda x: x["score"], reverse=True)
    return heat_tiles
