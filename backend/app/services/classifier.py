from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import numpy as np


class ArticleClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words="english")
        self.classifier = MultinomialNB()
        self.categories = {}
        self.is_trained = False

    def train(self, texts: List[str], labels: List[int]):
        X = self.vectorizer.fit_transform(texts)
        self.classifier.fit(X, labels)
        self.is_trained = True

    def predict(self, text: str) -> int:
        if not self.is_trained:
            return 0
        X = self.vectorizer.transform([text])
        return self.classifier.predict(X)[0]

    def classify_by_keywords(
        self, title: str, abstract: str, keywords: List[str]
    ) -> Dict[str, float]:
        text = f"{title} {abstract} {' '.join(keywords)}"

        keyword_categories = {
            "Artificial Intelligence": [
                "machine learning",
                "deep learning",
                "neural network",
                "AI",
                "algorithm",
            ],
            "Data Science": [
                "data analysis",
                "big data",
                "analytics",
                "statistics",
                "mining",
            ],
            "Medicine": ["medical", "disease", "treatment", "clinical", "health"],
            "Biology": ["cell", "gene", "protein", "organism", "species"],
            "Physics": ["quantum", "particle", "energy", "force", "relativity"],
        }

        scores = {}
        text_lower = text.lower()

        for category, keywords_list in keyword_categories.items():
            score = sum(1 for kw in keywords_list if kw in text_lower)
            scores[category] = score / len(keywords_list)

        return scores
