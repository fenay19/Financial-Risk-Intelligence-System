import re
import nltk
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# Ensure NLTK resources are available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Load specifically limited spacy model globally
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

INDIAN_STOPWORDS_EXTRA = {
    "crore", "lakh", "crores", "lakhs", "rs", "inr", "rupee", "rupees",
    "nse", "bse", "sensex", "nifty", "sebi", "rbi", "fy", "q1", "q2",
    "q3", "q4", "yoy", "qoq", "ipo", "fpo", "fii", "dii", "mf",
    "said", "also", "company", "share", "stock", "year", "quarter",
    "period", "result", "report", "statement", "mr", "ms", "ltd", "pvt"
}

stop_words = set(stopwords.words('english')).union(INDIAN_STOPWORDS_EXTRA)
stemmer = PorterStemmer()

INDIAN_ENTITY_LABELS = {
    "ORG", "GPE", "LAW", "MONEY", "PERSON", "EVENT"
}

def clean_text(text: str) -> str:
    """Removes standard noise while retaining monetary and structural syntax."""
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\n+', ' ', text)
    return text.strip()

def tokenize_and_stem(text: str) -> list[str]:
    """Tokenization and stemming specific to financial context."""
    text = clean_text(text).lower()
    # Filter non-alphanumeric but keeping dots for acronyms could be useful (omitted for brevity)
    tokens = word_tokenize(re.sub(r'[^a-z0-9\s]', '', text))
    return [stemmer.stem(t) for t in tokens if t not in stop_words and len(t) > 2]

def extract_financial_figures(text: str) -> list[dict]:
    """
    Extracts explicit financial references using regex arrays mapping to Indian market scales.
    Returns: [{'amount': str, 'unit': str, 'context': str}]
    """
    figures = []
    
    # Matching expressions like "Rs. 1,000 crore"
    pattern1 = r'(?:Rs\.?|INR|₹)\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(crore|lakh|crores|lakhs)?'
    # Matching expressions like "15.5 per cent decline"
    pattern2 = r'(\d+(?:\.\d+)?)\s*(?:per cent|percent|%)\s*(decline|fall|rise|growth|loss)'
    
    for match in re.finditer(pattern1, text, re.IGNORECASE):
        amount, unit = match.groups()
        figures.append({
            "amount": amount,
            "unit": unit.lower() if unit else "absolute",
            "context": "currency"
        })
        
    for match in re.finditer(pattern2, text, re.IGNORECASE):
        amount, context = match.groups()
        figures.append({
            "amount": amount,
            "unit": "%",
            "context": context.lower()
        })
        
    return figures

def extract_entities(text: str) -> dict[str, list[str]]:
    """
    Leverages spaCy NER mapped solely to the `en_core_web_sm` model and filters out elements into Indian contextual bins.
    """
    doc = nlp(text)
    entities = {label: [] for label in INDIAN_ENTITY_LABELS}
    
    for ent in doc.ents:
        if ent.label_ in INDIAN_ENTITY_LABELS:
            entities[ent.label_].append(ent.text)
            
    # Deduplicate
    for k in entities:
        entities[k] = list(set(entities[k]))
        
    return entities
