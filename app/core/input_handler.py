import re
from app.models import EntityResolution

TICKER_MAP = {
    "reliance": {
        "name": "Reliance Industries", "sector": "Conglomerate",
        "nse": "RELIANCE", "bse": "500325",
        "indices": ["NIFTY 50", "SENSEX", "NIFTY 500"],
        "extra_terms": ["RIL", "Mukesh Ambani", "Jio", "petrochemical", "retail", "O2C", "Green Energy"]
    },
    "tcs": {
        "name": "Tata Consultancy Services", "sector": "IT",
        "nse": "TCS", "bse": "532540",
        "indices": ["NIFTY 50", "SENSEX", "NIFTY IT"],
        "extra_terms": ["TCS", "IT services", "outsourcing", "Tata Group", "Rajesh Gopinathan", "digital transformation"]
    },
    "hdfcbank": {
        "name": "HDFC Bank", "sector": "Banking",
        "nse": "HDFCBANK", "bse": "500180",
        "indices": ["NIFTY 50", "SENSEX", "NIFTY Bank", "NIFTY Private Bank"],
        "extra_terms": ["HDFC", "NPA", "loan growth", "merger", "Sashidhar Jagdishan"]
    },
    "infy": {
        "name": "Infosys", "sector": "IT",
        "nse": "INFY", "bse": "500209",
        "indices": ["NIFTY 50", "SENSEX", "NIFTY IT"],
        "extra_terms": ["Infosys", "Salil Parekh", "attrition", "IT export", "visa", "US revenue"]
    },
    "icicibank": {
        "name": "ICICI Bank", "sector": "Banking",
        "nse": "ICICIBANK", "bse": "532174",
        "indices": ["NIFTY 50", "SENSEX", "NIFTY Bank"],
        "extra_terms": ["ICICI", "retail banking", "NPA", "Sandeep Bakhshi"]
    },
    "bajfinance": {
        "name": "Bajaj Finance", "sector": "NBFC",
        "nse": "BAJFINANCE", "bse": "500034",
        "indices": ["NIFTY 50", "NIFTY Financial Services"],
        "extra_terms": ["NBFC", "consumer lending", "RBI regulation", "Rajeev Jain", "AUM growth", "NPA"]
    },
    "wipro": {
        "name": "Wipro", "sector": "IT",
        "nse": "WIPRO", "bse": "507685",
        "indices": ["NIFTY 50", "NIFTY IT"],
        "extra_terms": ["Wipro", "Thierry Delaporte", "deal wins", "attrition"]
    },
    "hul": {
        "name": "Hindustan Unilever", "sector": "FMCG",
        "nse": "HINDUNILVR", "bse": "500696",
        "indices": ["NIFTY 50", "SENSEX", "NIFTY FMCG"],
        "extra_terms": ["HUL", "FMCG", "rural demand", "commodity cost", "Rohit Jawa", "volume growth"]
    },
    "itc": {
        "name": "ITC Limited", "sector": "FMCG / Tobacco",
        "nse": "ITC", "bse": "500875",
        "indices": ["NIFTY 50", "SENSEX"],
        "extra_terms": ["ITC", "tobacco", "cigarette tax", "GST", "FMCG diversification"]
    },
    "lnt": {
        "name": "Larsen & Toubro", "sector": "Infrastructure / Engineering",
        "nse": "LT", "bse": "500510",
        "indices": ["NIFTY 50", "SENSEX"],
        "extra_terms": ["L&T", "order book", "infra", "defense", "S.N. Subrahmanyan", "government contracts", "capex"]
    },
    "sunpharma": {
        "name": "Sun Pharmaceutical", "sector": "Pharmaceuticals",
        "nse": "SUNPHARMA", "bse": "524715",
        "indices": ["NIFTY 50", "NIFTY Pharma"],
        "extra_terms": ["Sun Pharma", "USFDA", "ANDA", "generic drugs", "Dilip Shanghvi", "US market"]
    },
    "adanient": {
        "name": "Adani Enterprises", "sector": "Conglomerate",
        "nse": "ADANIENT", "bse": "512599",
        "indices": ["NIFTY 50", "NIFTY 500"],
        "extra_terms": ["Adani", "Gautam Adani", "Hindenburg", "airport", "green energy", "port", "FPO"]
    },
    "ongc": {
        "name": "ONGC", "sector": "Oil & Gas",
        "nse": "ONGC", "bse": "500312",
        "indices": ["NIFTY 50", "SENSEX"],
        "extra_terms": ["crude oil", "gas production", "subsidy", "PSU", "energy transition", "OPEC"]
    },
    "sbi": {
        "name": "State Bank of India", "sector": "Banking (PSU)",
        "nse": "SBIN", "bse": "500112",
        "indices": ["NIFTY 50", "SENSEX", "NIFTY Bank", "NIFTY PSU Bank"],
        "extra_terms": ["SBI", "PSU bank", "government bank", "NPA", "Dinesh Kumar Khara", "priority sector lending"]
    },
    "maruti": {
        "name": "Maruti Suzuki", "sector": "Automobiles",
        "nse": "MARUTI", "bse": "532500",
        "indices": ["NIFTY 50", "SENSEX", "NIFTY Auto"],
        "extra_terms": ["Maruti", "Suzuki", "passenger vehicle", "EV transition", "chip shortage", "Hisashi Takeuchi"]
    },
    "tatamotors": {
        "name": "Tata Motors", "sector": "Automobiles",
        "nse": "TATAMOTORS", "bse": "500570",
        "indices": ["NIFTY 50", "NIFTY Auto"],
        "extra_terms": ["Tata Motors", "Jaguar Land Rover", "JLR", "EV", "Nexon", "N. Chandrasekaran"]
    },
    "axisbank": {
        "name": "Axis Bank", "sector": "Banking",
        "nse": "AXISBANK", "bse": "532215",
        "indices": ["NIFTY 50", "NIFTY Bank"],
        "extra_terms": ["Axis Bank", "Amitabh Chaudhry", "NPA", "Citibank acquisition"]
    },
    "kotak": {
        "name": "Kotak Mahindra Bank", "sector": "Banking",
        "nse": "KOTAKBANK", "bse": "500247",
        "indices": ["NIFTY 50", "NIFTY Bank"],
        "extra_terms": ["Kotak", "Uday Kotak", "RBI ban", "Ashok Vaswani", "digital banking"]
    },
    "dmart": {
        "name": "Avenue Supermarts (DMart)", "sector": "Retail",
        "nse": "DMART", "bse": "540376",
        "indices": ["NIFTY 50", "NIFTY 500"],
        "extra_terms": ["DMart", "supermarket", "Radhakishan Damani", "quick commerce", "Zepto", "Blinkit"]
    },
    "zomato": {
        "name": "Zomato", "sector": "Foodtech",
        "nse": "ZOMATO", "bse": "543320",
        "indices": ["NIFTY 500", "NIFTY Midcap 150"],
        "extra_terms": ["Zomato", "food delivery", "Blinkit", "quick commerce", "Deepinder Goyal", "Swiggy competition", "profitability"]
    },
    "drreddy": {"name": "Dr. Reddy's Laboratories", "sector": "Pharmaceuticals", "nse": "DRREDDY", "bse": "500124", "indices": ["NIFTY 50", "NIFTY Pharma"], "extra_terms": ["Dr Reddy", "USFDA", "generic"]},
    "cipla": {"name": "Cipla", "sector": "Pharmaceuticals", "nse": "CIPLA", "bse": "500087", "indices": ["NIFTY 50", "NIFTY Pharma"], "extra_terms": ["cipla", "respiratory", "inhalers"]},
    "divislab": {"name": "Divi's Laboratories", "sector": "Pharmaceuticals", "nse": "DIVISLAB", "bse": "532488", "indices": ["NIFTY 50", "NIFTY Pharma"], "extra_terms": ["Divis", "API", "custom synthesis"]},
    "hcltech": {"name": "HCL Technologies", "sector": "IT", "nse": "HCLTECH", "bse": "532281", "indices": ["NIFTY 50", "NIFTY IT"], "extra_terms": ["HCL", "software"]},
    "techm": {"name": "Tech Mahindra", "sector": "IT", "nse": "TECHM", "bse": "532755", "indices": ["NIFTY 50", "NIFTY IT"], "extra_terms": ["Tech Mahindra", "telecom IT"]},
    "mphasis": {"name": "Mphasis", "sector": "IT", "nse": "MPHASIS", "bse": "526299", "indices": ["NIFTY IT"], "extra_terms": ["Mphasis", "cloud"]},
    "bhel": {"name": "Bharat Heavy Electricals", "sector": "Capital Goods", "nse": "BHEL", "bse": "500103", "indices": ["NIFTY PSE"], "extra_terms": ["BHEL", "PSU", "power equipment"]},
    "coalindia": {"name": "Coal India", "sector": "Mining", "nse": "COALINDIA", "bse": "533278", "indices": ["NIFTY 50"], "extra_terms": ["coal", "mining", "CIL"]},
    "ntpc": {"name": "NTPC", "sector": "Power", "nse": "NTPC", "bse": "532555", "indices": ["NIFTY 50"], "extra_terms": ["thermal power", "renewables"]},
    "bpcl": {"name": "Bharat Petroleum", "sector": "Oil & Gas", "nse": "BPCL", "bse": "533106", "indices": ["NIFTY 50"], "extra_terms": ["refining", "fuel marketing"]},
    "muthootfin": {"name": "Muthoot Finance", "sector": "NBFC", "nse": "MUTHOOTFIN", "bse": "533398", "indices": ["NIFTY Financial Services"], "extra_terms": ["gold loan", "NBFC"]},
    "cholafin": {"name": "Cholamandalam Investment", "sector": "NBFC", "nse": "CHOLAFIN", "bse": "511243", "indices": ["NIFTY Financial Services"], "extra_terms": ["vehicle finance", "Murugappa"]},
    "ultracemco": {"name": "UltraTech Cement", "sector": "Cement", "nse": "ULTRACEMCO", "bse": "532538", "indices": ["NIFTY 50"], "extra_terms": ["UltraTech", "cement", "construction"]},
    "acc": {"name": "ACC", "sector": "Cement", "nse": "ACC", "bse": "500410", "indices": ["NIFTY Next 50"], "extra_terms": ["ACC", "Adani cement"]},
    "siemens": {"name": "Siemens", "sector": "Capital Goods", "nse": "SIEMENS", "bse": "500550", "indices": ["NIFTY Next 50"], "extra_terms": ["automation", "industrial"]},
    "paytm": {"name": "One97 Communications (Paytm)", "sector": "Fintech", "nse": "PAYTM", "bse": "543396", "indices": ["NIFTY Next 50"], "extra_terms": ["Paytm", "Vijay Shekhar Sharma", "RBI ban"]},
    "nykaa": {"name": "FSN E-Commerce Ventures (Nykaa)", "sector": "E-Commerce", "nse": "NYKAA", "bse": "543384", "indices": ["NIFTY Next 50"], "extra_terms": ["Nykaa", "beauty", "fashion"]},
    "policybzr": {"name": "PB Fintech (PolicyBazaar)", "sector": "Fintech", "nse": "POLICYBZR", "bse": "543390", "indices": ["NIFTY Next 50"], "extra_terms": ["PolicyBazaar", "insurance"]},
    "hal": {"name": "Hindustan Aeronautics", "sector": "Defence", "nse": "HAL", "bse": "541154", "indices": ["NIFTY Next 50"], "extra_terms": ["HAL", "defence", "Tejas"]},
    "bel": {"name": "Bharat Electronics", "sector": "Defence", "nse": "BEL", "bse": "500049", "indices": ["NIFTY Next 50"], "extra_terms": ["BEL", "radar", "defence electronics"]},
    "mtar": {"name": "MTAR Technologies", "sector": "Defence & Aerospace", "nse": "MTARTECH", "bse": "543270", "indices": ["NIFTY Smallcap 250"], "extra_terms": ["MTAR", "precision engineering"]}
}

SECTOR_MAP = {
    "banking": {
        "terms": ["NPA", "net interest margin", "NIM", "repo rate", "RBI", "credit growth", "CASA ratio", "loan book", "GNPA", "NNPA", "priority sector", "SLR", "CRR", "Basel III", "CRAR", "PSU bank", "private bank", "NBFC", "microfinance"],
        "key_stocks": ["HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK"]
    },
    "it": {
        "terms": ["US recession", "client spending", "attrition", "visa H1B", "NASSCOM", "digital transformation", "deal wins", "TCV", "offshoring", "INR depreciation benefit", "cloud migration", "margin pressure", "fresher hiring", "subcontracting"],
        "key_stocks": ["TCS", "INFY", "WIPRO", "HCLTECH", "TECHM"]
    },
    "pharma": {
        "terms": ["USFDA", "CDSCO", "import alert", "warning letter", "ANDA", "drug approval", "patent cliff", "API", "formulation", "generic pricing", "price erosion", "EMA", "WHO-GMP", "inspection", "recall", "clinical trial", "PLI scheme"],
        "key_stocks": ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "AUROPHARMA"]
    },
    "auto": {
        "terms": ["wholesale", "retail sales", "OEM", "EV transition", "FAME", "BS6", "PLI auto", "chip shortage", "lithium battery", "two wheeler", "PV segment", "tractor demand", "export", "steel cost", "commodity input"],
        "key_stocks": ["MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO", "HEROMOTOCO"]
    },
    "fmcg": {
        "terms": ["rural demand", "urban consumption", "commodity inflation", "palm oil", "crude derivative", "GST", "volume growth", "price hike", "distribution", "modern trade", "e-commerce", "Dabur", "HUL", "ITC", "branded market"],
        "key_stocks": ["HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "DABUR"]
    },
    "nbfc": {
        "terms": ["AUM", "cost of funds", "asset quality", "GNPA", "write-off", "RBI regulation", "liquidity", "co-lending", "microfinance", "gold loan", "vehicle finance", "IL&FS", "DHFL", "credit rating"],
        "key_stocks": ["BAJFINANCE", "MUTHOOTFIN", "CHOLAFIN", "M&MFIN"]
    },
    "infra": {
        "terms": ["order book", "government capex", "NHI", "NHAI", "road", "railway", "smart city", "PLI scheme", "execution", "working capital", "L1 bid", "project delay", "land acquisition", "environment clearance"],
        "key_stocks": ["LT", "ULTRACEMCO", "BHEL", "NTPC", "SIEMENS"]
    },
    "energy": {
        "terms": ["crude oil", "Brent", "WTI", "OPEC", "natural gas", "LNG", "refinery margin", "GRM", "subsidy", "energy transition", "renewables", "solar", "wind", "CERC", "power tariff", "under-recovery", "fuel pricing", "PSU oil"],
        "key_stocks": ["RELIANCE", "ONGC", "BPCL", "IOC", "NTPC"]
    },
    "realty": {
        "terms": ["housing demand", "RERA", "unsold inventory", "launches", "affordable housing", "interest rate sensitivity", "home loan", "NHB", "project delay", "land cost", "construction cost", "stamp duty", "FSI"],
        "key_stocks": ["DLF", "GODREJPROP", "PRESTIGE", "OBEROIRLTY"]
    },
}

NIFTY_INDICES = {
    "nifty bank": "banking",
    "nifty it": "it",
    "nifty pharma": "pharma",
    "nifty auto": "auto",
    "nifty fmcg": "fmcg",
    "nifty energy": "energy",
    "nifty infra": "infra",
    "nifty realty": "realty",
    "nifty financial services": "nbfc" # approximation for mapping key stocks
}

async def resolve_entity(user_input: str) -> EntityResolution:
    """
    Resolves arbitrary user input into structured entity parameters using local 
    lookups focusing on core Indian equities, sectors, and indices.
    """
    normalized_input = re.sub(r'[^a-zA-Z0-9\s]', '', user_input).strip().lower()

    # 1. Exact match against TICKER_MAP keys or NSE ticker
    for key, data in TICKER_MAP.items():
        if normalized_input == key or normalized_input == data["nse"].lower():
            return EntityResolution(
                type="stock",
                ticker_nse=data["nse"],
                ticker_bse=data["bse"],
                company_name=data["name"],
                sector=data["sector"],
                index_membership=data["indices"],
                search_terms=data["extra_terms"] + [data["name"], data["nse"]]
            )

    # 2. Contains match on company names
    for key, data in TICKER_MAP.items():
        if normalized_input in data["name"].lower():
            return EntityResolution(
                type="stock",
                ticker_nse=data["nse"],
                ticker_bse=data["bse"],
                company_name=data["name"],
                sector=data["sector"],
                index_membership=data["indices"],
                search_terms=data["extra_terms"] + [data["name"], data["nse"]]
            )

    # 3. Match against explicitly tracked NIFTY indices
    for index_name, target_sector in NIFTY_INDICES.items():
        if normalized_input == index_name:
            sector_data = SECTOR_MAP[target_sector]
            return EntityResolution(
                type="index",
                ticker_nse=None,
                ticker_bse=None,
                company_name=index_name.upper(),
                sector=target_sector.capitalize(),
                index_membership=[],
                search_terms=sector_data["terms"] + sector_data["key_stocks"]
            )

    # 4. Check against Sector Map
    for sector, details in SECTOR_MAP.items():
        if sector in normalized_input:
            return EntityResolution(
                type="sector",
                ticker_nse=None,
                ticker_bse=None,
                company_name=f"{sector.capitalize()} Sector",
                sector=sector.capitalize(),
                index_membership=[],
                search_terms=details["terms"] + details["key_stocks"]
            )

    # 5. Fallback Freetext
    return EntityResolution(
        type="freetext",
        ticker_nse=None,
        ticker_bse=None,
        company_name=user_input,
        sector=None,
        index_membership=[],
        search_terms=[user_input]
    )
