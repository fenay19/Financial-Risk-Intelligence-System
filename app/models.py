from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EntityResolution(BaseModel):
    """
    Resolved details for a user's input querying a specific entity on the Indian market.
    """
    type: str               # "stock" | "sector" | "index" | "freetext"
    ticker_nse: Optional[str] = None   # e.g. "RELIANCE"
    ticker_bse: Optional[str] = None   # e.g. "500325"
    company_name: str
    sector: Optional[str] = None
    index_membership: list[str]  # e.g. ["NIFTY 50", "NIFTY 500"]
    search_terms: list[str]

class RawDocument(BaseModel):
    """
    A unified structure representing a raw document from an external data source.
    """
    source: str       # "MoneycontrolRSS"|"BSEFiling"|"NSEFiling"|"SEBI"|"YFinance"
    title: str
    text: str
    url: Optional[str] = None
    published_at: Optional[datetime] = None

class CategoryRisk(BaseModel):
    """
    Score and breakdown for a specific category pattern.
    """
    score: float
    label: str
    top_triggers: list[str]

class RiskSentence(BaseModel):
    """
    A single critically flagged sentence within a document mapped back to an origin.
    """
    text: str
    source: str
    published_at: Optional[str] = None
    category: str
    risk_score: float

class MarketMetrics(BaseModel):
    """
    Financial aggregates focusing heavily on variables impacting Indian market fundamentals.
    """
    beta: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    roe: Optional[float] = None
    promoter_holding: Optional[float] = None   # Indian-specific: promoter % holding
    pledged_shares_pct: Optional[float] = None # Indian-specific: % shares pledged
    india_vix: Optional[float] = None          # India VIX at time of analysis
    usd_inr_rate: Optional[float] = None       # live USD/INR
    repo_rate: Optional[float] = None          # RBI repo rate
    revenue_growth_yoy: Optional[float] = None
    market_cap_cr: Optional[float] = None      # Market cap in INR Crores

class RiskReport(BaseModel):
    """
    Comprehensive payload documenting overall risk profile following analysis.
    """
    query: str
    entity: EntityResolution
    risk_score: float
    risk_label: str
    risk_delta: Optional[float] = None
    category_breakdown: dict[str, CategoryRisk]
    top_sentences: list[RiskSentence]
    top_risk_terms: list[str]
    market_metrics: MarketMetrics
    documents_analyzed: int
    analysis_timestamp: datetime
    disclaimer: str = ("This is an AI-generated risk analysis tool for "
                       "informational purposes only. Not SEBI-registered "
                       "investment advice.")

class AnalyzeRequest(BaseModel):
    """
    Request model for the analysis endpoint to specify target and refresh cache config.
    """
    q: str
    refresh: bool = False
