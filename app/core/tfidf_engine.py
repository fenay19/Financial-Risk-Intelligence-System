import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.core.risk_lexicon import LEXICON
from app.core.preprocessor import clean_text

class TFIDFEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000, ngram_range=(1, 2))
        
        # Prepare category documents
        self.categories = list(LEXICON.keys())
        self.category_texts = [" ".join(LEXICON[cat]) for cat in self.categories]
        
        # Fit vectorizer on category data to ensure vocabulary encompasses risk terms
        self.vectorizer.fit(self.category_texts)
        self.category_vectors = self.vectorizer.transform(self.category_texts)

    def extract_top_terms(self, docs_text: list[str], top_n: int = 20) -> list[str]:
        """Extract globally prominent TF-IDF terms from the provided texts."""
        if not docs_text:
            return []
            
        combined_text = " ".join([clean_text(t) for t in docs_text])
        try:
            vec = TfidfVectorizer(stop_words='english', max_features=100)
            X = vec.fit_transform([combined_text])
            
            indices = np.argsort(X.toarray()[0])[::-1]
            features = vec.get_feature_names_out()
            return [features[i] for i in indices[:top_n]]
        except Exception:
            return []

    def classify_sentence(self, sentence: str) -> tuple[str, float, list[str]]:
        """
        Classifies a single sentence against risk categories based on Cosine Similarity.
        Returns: (category, similarity_score, matched_terms)
        """
        cleaned = clean_text(sentence)
        if not cleaned:
            return ("NONE", 0.0, [])
            
        sent_vec = self.vectorizer.transform([cleaned])
        sims = cosine_similarity(sent_vec, self.category_vectors)[0]
        
        best_idx = np.argmax(sims)
        best_score = sims[best_idx]
        
        if best_score < 0.05: # threshold
            return ("NONE", 0.0, [])
            
        best_cat = self.categories[best_idx]
        
        # Extract matched triggers
        matched_terms = [term for term in LEXICON[best_cat] if term.lower() in cleaned.lower()]
        
        return (best_cat, float(best_score), matched_terms)
