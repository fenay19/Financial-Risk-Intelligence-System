import re
from app.core.preprocessor import clean_text

# A simple lexicon for financial sentiment
NEGATIVE_WORDS = {
    "raid", "seizure", "attachment", "diversion", "siphon", "tunneling",
    "pledged", "forced sale", "margin call", "slippage", "NPA", "default",
    "demonetization", "lockdown", "ban", "strike", "agitation", "slowdown",
    "import alert", "warning letter", "qualified opinion", "going concern",
    "promoter exit", "FPI exit", "circuit", "lower circuit", "suspension",
    "loss", "decline", "fall", "downgrade", "debt", "lawsuit", "penalty",
    "resigned", "quit", "violation", "breach", "fail", "missed", "weak",
    "poor", "slump", "plunge", "crash", "bear", "negative", "warns", "delay"
}

POSITIVE_WORDS = {
    "PLI benefit", "order win", "capacity expansion", "export growth",
    "FII buying", "DII buying", "upgrade", "target price raised",
    "dividend", "buyback", "debt free", "zero debt", "cash rich",
    "strong order book", "record revenue", "beat estimate", "PAT growth",
    "EBITDA expansion", "market share gain", "promoter buying",
    "demerger value unlock", "listing gain", "bonus issue",
    "profit", "growth", "rise", "jump", "surge", "gain", "beat", "strong",
    "upward", "bull", "positive", "approval", "clearance", "win", "success"
}

def is_multi_word_match(term: str, text: str) -> bool:
    """Checks for multi-word phrases explicitly."""
    return f" {term.lower()} " in f" {text.lower()} "

def score_sentiment(text: str) -> float:
    """
    Computes a base sentiment score mapping.
    Returns: A float between -1.0 and 1.0
    """
    cleaned = clean_text(text).lower()
    
    pos_count = 0
    neg_count = 0
    
    for term in POSITIVE_WORDS:
        if " " in term:
            if is_multi_word_match(term, cleaned): pos_count += 2
        else:
            if re.search(rf'\b{term}\b', cleaned): pos_count += 1
            
    for term in NEGATIVE_WORDS:
        if " " in term:
            if is_multi_word_match(term, cleaned): neg_count += 2
        else:
            if re.search(rf'\b{term}\b', cleaned): neg_count += 1
            
    total = pos_count + neg_count
    if total == 0:
        return 0.0
        
    return (pos_count - neg_count) / total
