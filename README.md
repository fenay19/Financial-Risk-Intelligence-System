# Indian Market Risk Intelligence System

This is a custom risk intelligence API and dashboard explicitly tuned to analyzing Indian equity markets. 

## Setup Instructions

1. **Install Requirements**
```bash
pip install -r requirements.txt
```

2. **Download NLP Spacy and NLTK primitives**
```bash
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt stopwords averaged_perceptron_tagger
```

3. **Provide Environmental Configuration**
```bash
cp .env.example .env
```
_Note: `NEWS_API_KEY` is optional — the system works without it using free RSS feeds from Indian business news providers._
_NSE and BSE APIs utilized internally are free and require no API key._

4. **Launch the Server**
```bash
uvicorn app.main:app --reload --port 8000
```
Open `http://localhost:8000` to access the main dashboard.

## Disclaimer

This tool is for informational purposes only. It is NOT registered investment advice under SEBI (Investment Advisers) Regulations, 2013. Always consult a SEBI-registered advisor before making investment decisions.
