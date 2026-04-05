import sqlite3
import os
import json
from datetime import datetime, timedelta
import pytz

IST = pytz.timezone("Asia/Kolkata")
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "risk_cache.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS risk_cache (
            query TEXT PRIMARY KEY,
            payload TEXT,
            score REAL,
            india_vix REAL,
            usd_inr REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_cached_report(query: str, ttl_hours: int = 4):
    """Retrieves an unexpired report."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT payload, timestamp FROM risk_cache WHERE query = ?", (query.lower(),))
    row = cur.fetchone()
    conn.close()
    
    if row:
        cached_time = datetime.fromisoformat(row[1])
        if datetime.now(IST) - cached_time < timedelta(hours=ttl_hours):
            return json.loads(row[0])
    return None

def save_to_cache(query: str, report: dict, score: float, india_vix: float, usd_inr: float):
    """Saves a generated report snapshot."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    tz_now = datetime.now(IST).isoformat()
    
    cur.execute('''
        INSERT INTO risk_cache (query, payload, score, india_vix, usd_inr, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(query) DO UPDATE SET 
            payload=excluded.payload,
            score=excluded.score,
            india_vix=excluded.india_vix,
            usd_inr=excluded.usd_inr,
            timestamp=excluded.timestamp
    ''', (query.lower(), json.dumps(report), score, india_vix, usd_inr, tz_now))
    
    conn.commit()
    conn.close()
    
def get_deltas(query: str) -> float:
    """Mockup to retrieve delta relative to last pull."""
    return 0.0
