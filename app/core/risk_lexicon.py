REGULATORY_RISK = [
    "SEBI order", "SEBI investigation", "show cause notice", "adjudication",
    "settlement order", "consent order", "interim order", "debarment",
    "trading ban", "market manipulation", "insider trading", "front running",
    "circuit breaker", "ASM", "GSM", "surveillance", "MCA notice",
    "NCLT", "IBC", "insolvency petition", "corporate fraud", "CBI probe",
    "ED raid", "income tax raid", "penalty", "fine", "RBI penalty",
    "PCA framework", "prompt corrective action", "license cancellation",
    "IRDAI", "CCI penalty", "merger blocked", "TRAI", "spectrum",
    "environment clearance rejected", "NGT order", "PIL", "court stay",
    "government audit", "CAG report", "vigilance", "disinvestment risk"
]

GEOPOLITICAL_RISK = [
    "India-China border", "LAC tension", "India-Pakistan", "Kashmir",
    "trade war", "US tariff", "China+1", "supply chain shift",
    "FDI restriction", "FPI outflow", "FATF", "OFAC sanction",
    "geopolitical tension", "crude oil price", "OPEC cut", "Russia-Ukraine",
    "Middle East conflict", "Strait of Hormuz", "election uncertainty",
    "state election", "general election", "policy uncertainty",
    "coalition government", "political instability", "protest",
    "farmer agitation", "economic nationalism", "import duty hike",
    "export ban", "wheat export ban", "steel export duty"
]

FINANCIAL_RISK = [
    "NPA", "GNPA", "NNPA", "gross NPA", "net NPA", "slippage",
    "provisioning", "PCR", "credit cost", "write-off", "debt restructuring",
    "one-time settlement", "IBC filing", "debt default", "payment default",
    "downgrade", "credit rating downgrade", "CRISIL downgrade", "ICRA downgrade",
    "outlook negative", "watch negative", "leverage", "debt to equity",
    "cash flow negative", "working capital stress", "liquidity crunch",
    "promoter pledge", "pledged shares", "margin call", "block deal",
    "bulk deal", "promoter selling", "insider sell", "earnings miss",
    "revenue miss", "EBITDA decline", "margin compression", "forex loss",
    "currency hedging", "mark to market loss", "goodwill impairment",
    "inventory write-down", "auditor qualification", "qualified accounts",
    "going concern", "restatement", "audit delay", "auditor change"
]

OPERATIONAL_RISK = [
    "plant shutdown", "factory fire", "industrial accident", "blast",
    "explosion", "pollution violation", "PCB notice", "CPCB",
    "supply disruption", "raw material shortage", "power outage",
    "strike", "lockout", "labour unrest", "worker agitation",
    "key management exit", "MD resignation", "CFO change", "auditor exit",
    "data breach", "cyberattack", "system failure", "IT outage",
    "fraud", "embezzlement", "diversion of funds", "shell company",
    "related party transaction", "RPT abuse", "promoter loan",
    "contingent liability", "GST notice", "customs duty dispute",
    "anti-dumping", "product recall", "quality failure", "export rejection",
    "USFDA import alert", "drug recall India", "drug ban"
]

COMPETITIVE_RISK = [
    "market share loss", "competition intensification", "Jio effect",
    "quick commerce threat", "Amazon India", "Flipkart", "price war",
    "margin pressure", "new entrant", "Chinese competition", "dumping",
    "commoditization", "PLI competitor", "startup disruption",
    "platform competition", "aggregator model", "D2C brand threat",
    "switching cost low", "customer churn", "talent attrition",
    "patent expiry", "brand erosion", "pricing power loss",
    "derating", "sector rotation", "FII selling", "DII selling"
]

ESG_RISK = [
    "carbon emission", "net zero India", "climate risk", "environmental",
    "pollution", "PCB", "CPCB violation", "river pollution", "water scarcity",
    "coal dependency", "thermal power", "stranded asset", "ESG rating",
    "BRSR", "Business Responsibility Report", "sustainability",
    "corporate governance", "board independence", "RPT", "related party",
    "promoter tunneling", "minority shareholder rights", "AGM controversy",
    "proxy advisory", "IiAS", "Stakeholders Empowerment Services",
    "CSR violation", "child labour", "human rights", "supply chain ESG",
    "gender diversity", "greenwashing India", "climate litigation"
]

INDIA_MACRO_RISK = [
    "RBI policy", "repo rate hike", "rate cut", "monetary policy",
    "inflation", "CPI", "WPI", "food inflation", "core inflation",
    "fiscal deficit", "current account deficit", "CAD",
    "rupee depreciation", "INR weakness", "currency risk",
    "FPI outflow", "FII selling", "dollar strengthening",
    "US Fed rate", "global recession", "India GDP slowdown",
    "IIP data", "PMI contraction", "credit growth slowdown",
    "monsoon failure", "kharif crop", "rabi crop", "agri stress",
    "fuel price hike", "LPG price", "petrol diesel", "subsidy burden",
    "disinvestment target", "fiscal slippage", "Union Budget",
    "GST collection", "direct tax", "advance tax", "TDS",
    "FEMA violation", "forex reserve decline", "BoP stress"
]

CATEGORY_WEIGHTS = {
    "REGULATORY":   0.22,
    "GEOPOLITICAL": 0.12,
    "FINANCIAL":    0.25,
    "OPERATIONAL":  0.13,
    "COMPETITIVE":  0.10,
    "ESG":          0.08,
    "INDIA_MACRO":  0.10
}

LEXICON = {
    "REGULATORY": REGULATORY_RISK,
    "GEOPOLITICAL": GEOPOLITICAL_RISK,
    "FINANCIAL": FINANCIAL_RISK,
    "OPERATIONAL": OPERATIONAL_RISK,
    "COMPETITIVE": COMPETITIVE_RISK,
    "ESG": ESG_RISK,
    "INDIA_MACRO": INDIA_MACRO_RISK
}
