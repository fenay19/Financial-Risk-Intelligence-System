from typing import Optional
from app.models import MarketMetrics, RiskSentence, CategoryRisk
from app.core.risk_lexicon import CATEGORY_WEIGHTS

def compute_india_market_boost(market_metrics: MarketMetrics,
                               surveillance_flag: Optional[str],
                               sebi_action_flag: bool) -> float:
    """
    Applies aggressive scaling factors matching Indian trading realities.
    """
    boost = 0.0
    
    # Financial ratio signals
    if market_metrics.beta and market_metrics.beta > 1.5: 
        boost += 5.0
    if market_metrics.debt_to_equity and market_metrics.debt_to_equity > 2.0:
        boost += 6.0
    if market_metrics.current_ratio and market_metrics.current_ratio < 1.0:
        boost += 5.0
    if market_metrics.roe and market_metrics.roe < 0: 
        boost += 4.0
        
    # India-specific market signals
    if market_metrics.pledged_shares_pct:
        if market_metrics.pledged_shares_pct > 30: boost += 12.0
        elif market_metrics.pledged_shares_pct > 15: boost += 6.0
        
    if market_metrics.promoter_holding:
        if market_metrics.promoter_holding < 25: boost += 8.0
        elif market_metrics.promoter_holding < 40: boost += 3.0
        
    # Surveillance flags (ASM/GSM = serious risk in Indian markets)
    if surveillance_flag == "GSM": boost += 20.0   # GSM is more severe
    elif surveillance_flag == "ASM": boost += 15.0
    
    # Active SEBI order
    if sebi_action_flag: boost += 18.0
    
    # India VIX (market fear index)
    if market_metrics.india_vix:
        if market_metrics.india_vix > 30: boost += 12.0
        elif market_metrics.india_vix > 20: boost += 6.0
        
    # INR depreciation signal (if usd_inr > 85 = pressure zone)
    if market_metrics.usd_inr_rate and market_metrics.usd_inr_rate > 85:
        boost += 4.0
        
    return min(boost, 25.0)   # cap boost at 25 points

def get_risk_label(score: float) -> str:
    if score >= 75:
        return "Severe Risk"
    elif score >= 50:
        return "High Risk"
    elif score >= 25:
        return "Moderate Risk"
    return "Low Risk"

def calculate_overall_risk(sentences: list[RiskSentence], 
                           market_metrics: MarketMetrics,
                           surveillance_flag: Optional[str],
                           sebi_flag: bool) -> tuple[float, dict[str, CategoryRisk]]:
    """
    Computes an aggregated risk profile merging NLP outcomes with market metrics.
    """
    # 1. Aggregate sentence scores into categories
    cat_aggs = {cat: {"sc": 0.0, "count": 0, "triggers": set()} for cat in CATEGORY_WEIGHTS.keys()}
    
    for s in sentences:
        if s.category in cat_aggs:
            cat_aggs[s.category]["sc"] += s.risk_score
            cat_aggs[s.category]["count"] += 1
            # Very rough trigger extraction from sentence score > 0 -> passed externally
            
    # Normalize category scores to 0-100 range and assemble output
    cat_breakdown = {}
    base_score = 0.0
    
    for cat, data in cat_aggs.items():
        # Using a bounded log scaling for text intensity
        normalized_cat_score = min(100.0, data["sc"] * 10) 
        
        cat_breakdown[cat] = CategoryRisk(
            score=normalized_cat_score,
            label=get_risk_label(normalized_cat_score),
            top_triggers=list(data["triggers"])[:5]
        )
        
        base_score += normalized_cat_score * CATEGORY_WEIGHTS.get(cat, 0)
        
    # 2. Add India Market Boost
    boost = compute_india_market_boost(market_metrics, surveillance_flag, sebi_flag)
    
    final_score = min(100.0, base_score + boost)
    return round(final_score, 2), cat_breakdown
