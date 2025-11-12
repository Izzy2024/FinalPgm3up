import logging
import os
import re
from typing import Optional, Tuple, List

import numpy as np
import pdfplumber
import requests
from sklearn.feature_extraction.text import TfidfVectorizer

from app.models.article import Article

logger = logging.getLogger(__name__)


class ArticleSummarizer:
    """
    Provides both local extractive summarization and Groq-powered abstractive summaries.
    """

    def __init__(self, groq_api_key: Optional[str] = None, groq_model: str = "llama-3.3-70b-versatile"):
        self.groq_api_key = groq_api_key
        self.groq_model = groq_model
        self.max_input_chars = 12000

    def summarize_article(
        self,
        article: Article,
        method: str = "auto",
        max_sentences: int = 5,
        max_pages: int = 5,
    ) -> Tuple[str, str]:
        text = self.get_article_text(article, max_pages=max_pages)
        if not text:
            raise ValueError("No text content available for summarization.")

        return self.summarize_text(text, method=method, max_sentences=max_sentences)

    def summarize_text(
        self,
        text: str,
        method: str = "auto",
        max_sentences: int = 5,
    ) -> Tuple[str, str]:
        cleaned = self._prepare_text(text)
        if not cleaned:
            raise ValueError("Provided text is empty after cleaning.")

        chosen_method = method
        if method == "auto":
            chosen_method = "groq" if self.groq_api_key else "local"

        if chosen_method == "groq":
            if not self.groq_api_key:
                raise ValueError("Groq API key is not configured.")
            summary = self._summarize_with_groq(cleaned)
            return summary, "groq"

        summary = self._summarize_extractive(cleaned, max_sentences=max_sentences)
        return summary, "local"

    def get_article_text(self, article: Article, max_pages: int = 5) -> str:
        parts: List[str] = []

        if article.abstract:
            parts.append(article.abstract.strip())

        if article.keywords:
            parts.append("Keywords: " + ", ".join(article.keywords[:10]))

        if article.file_path and os.path.exists(article.file_path):
            try:
                file_text = self._read_file_excerpt(article.file_path, max_pages=max_pages)
                if file_text:
                    parts.append(file_text)
            except Exception as exc:
                logger.warning("Failed to read article file for summarization: %s", exc)

        combined = "\n".join(part for part in parts if part).strip()
        if len(combined) > self.max_input_chars:
            combined = combined[: self.max_input_chars]
        return combined

    def _read_file_excerpt(self, file_path: str, max_pages: int = 5) -> str:
        if file_path.lower().endswith(".txt"):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(self.max_input_chars)

        if file_path.lower().endswith(".pdf"):
            texts: List[str] = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages[:max_pages]:
                    page_text = page.extract_text()
                    if page_text:
                        texts.append(page_text)
            return "\n".join(texts)

        return ""

    def _prepare_text(self, text: str) -> str:
        cleaned = re.sub(r"\s+", " ", text).strip()
        if len(cleaned) > self.max_input_chars:
            cleaned = cleaned[: self.max_input_chars]
        return cleaned

    def _summarize_extractive(self, text: str, max_sentences: int = 5) -> str:
        sentences = self._split_sentences(text)
        if not sentences:
            raise ValueError("Unable to detect sentences for summarization.")
        if len(sentences) <= max_sentences:
            return " ".join(sentences)

        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(sentences)
        # Score each sentence by summing TF-IDF weights of its terms
        sentence_scores = tfidf_matrix.sum(axis=1).A1
        top_indices = np.argsort(sentence_scores)[::-1][:max_sentences]
        top_indices_sorted = sorted(top_indices)
        selected_sentences = [sentences[idx].strip() for idx in top_indices_sorted]
        return " ".join(selected_sentences)

    def _split_sentences(self, text: str) -> List[str]:
        potential = re.split(r"(?<=[.!?])\s+", text)
        return [sentence.strip() for sentence in potential if len(sentence.strip()) > 20]

    def _summarize_with_groq(self, text: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.groq_model,
            "temperature": 0.3,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an expert research assistant. "
                        "Produce concise academic summaries highlighting objectives, methods, key findings, and implications."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Summarize the following scientific article in 5 bullet points, each under 35 words. "
                        "Focus on purpose, methodology, results, and significance.\n\n"
                        f"Article text:\n{text}"
                    ),
                },
            ],
        }

        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            choices = data.get("choices", [])
            if not choices:
                raise ValueError("Groq API returned no completion choices.")
            content = choices[0]["message"]["content"]
            return content.strip()
        except requests.RequestException as exc:
            raise RuntimeError(f"Groq API request failed: {exc}") from exc
