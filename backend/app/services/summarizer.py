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
    Provides multi-level summarization (executive, detailed, exhaustive)
    with both local extractive and Groq-powered abstractive summaries.
    """

    def __init__(self, groq_api_key: Optional[str] = None, groq_model: str = "llama-3.3-70b-versatile"):
        self.groq_api_key = groq_api_key
        self.groq_model = groq_model
        self.max_input_chars = 50000  # Increased from 12000 to support full documents

        # Configuration per level
        self.level_config = {
            "executive": {
                "target_words": 500,
                "max_pages": 20,
                "max_sentences": 10,
            },
            "detailed": {
                "target_words": 1800,
                "max_pages": 50,
                "max_sentences": 30,
            },
            "exhaustive": {
                "target_words": 4000,
                "max_pages": 100,
                "max_sentences": 60,
            }
        }

    def summarize_article(
        self,
        article: Article,
        method: str = "auto",
        max_sentences: int = 5,
        max_pages: int = 5,
        level: str = "detailed",
    ) -> Tuple[str, str]:
        """
        Summarize an article at the specified level.

        Args:
            article: Article to summarize
            method: "auto", "groq", or "local"
            max_sentences: For local method
            max_pages: Pages to process
            level: "executive", "detailed", or "exhaustive"
        """
        config = self.level_config.get(level, self.level_config["detailed"])
        text = self.get_article_text(article, max_pages=config["max_pages"])
        if not text:
            raise ValueError("No text content available for summarization.")

        return self.summarize_text(
            text,
            method=method,
            max_sentences=config["max_sentences"],
            level=level
        )

    def summarize_text(
        self,
        text: str,
        method: str = "auto",
        max_sentences: int = 5,
        level: str = "detailed",
    ) -> Tuple[str, str]:
        """
        Summarize text at specified level.

        Args:
            text: Text to summarize
            method: "auto", "groq", or "local"
            max_sentences: For local method
            level: "executive", "detailed", or "exhaustive"
        """
        cleaned = self._prepare_text(text)
        if not cleaned:
            raise ValueError("Provided text is empty after cleaning.")

        chosen_method = method
        if method == "auto":
            chosen_method = "groq" if self.groq_api_key else "local"

        if chosen_method == "groq":
            if not self.groq_api_key:
                raise ValueError("Groq API key is not configured.")
            summary = self._summarize_with_groq(cleaned, level=level)
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

    def _get_prompt_for_level(self, level: str) -> dict:
        """Get system and user prompt templates for the specified level."""

        prompts = {
            "executive": {
                "system": (
                    "Eres un asistente experto en investigación académica. "
                    "Crea resúmenes ejecutivos concisos pero informativos de artículos científicos."
                ),
                "user": (
                    "Crea un RESUMEN EJECUTIVO del siguiente artículo científico.\n\n"
                    "FORMATO REQUERIDO:\n"
                    "# Resumen Ejecutivo\n\n"
                    "## Problema de Investigación\n"
                    "[2 párrafos: ¿Qué problema aborda esta investigación? ¿Por qué es importante?]\n\n"
                    "## Metodología\n"
                    "[1 párrafo: ¿Qué enfoque se utilizó para investigar el problema?]\n\n"
                    "## Hallazgos Clave\n"
                    "- [Hallazgo 1 con datos de soporte]\n"
                    "- [Hallazgo 2 con datos de soporte]\n"
                    "- [Hallazgo 3 con datos de soporte]\n"
                    "- [Hallazgo 4 si aplica]\n\n"
                    "## Conclusión Principal\n"
                    "[1 párrafo: ¿Cuál es la conclusión principal?]\n\n"
                    "Usa lenguaje académico claro. Sé específico con números y resultados.\n"
                    "Longitud objetivo: 500 palabras.\n\n"
                    "ARTÍCULO:\n{text}"
                )
            },
            "detailed": {
                "system": (
                    "Eres un asistente experto en investigación académica. "
                    "Crea resúmenes detallados y estructurados que capturen todos los aspectos importantes de artículos científicos."
                ),
                "user": (
                    "Crea un RESUMEN DETALLADO (3-4 páginas) del siguiente artículo científico.\n\n"
                    "FORMATO REQUERIDO:\n"
                    "# Resumen Detallado\n\n"
                    "## Introducción y Contexto\n"
                    "[2-3 párrafos explicando el contexto, la motivación y el vacío en la literatura]\n\n"
                    "## Objetivos y Preguntas de Investigación\n"
                    "- [Objetivo 1]\n"
                    "- [Objetivo 2]\n"
                    "- [Hipótesis si aplica]\n\n"
                    "## Metodología\n"
                    "### Diseño del Estudio\n"
                    "[1-2 párrafos sobre el diseño de investigación]\n\n"
                    "### Muestra y Participantes\n"
                    "[1 párrafo sobre quién/qué fue estudiado, tamaño de muestra, criterios]\n\n"
                    "### Recolección de Datos\n"
                    "- [Instrumento 1: descripción]\n"
                    "- [Instrumento 2: descripción]\n\n"
                    "### Métodos de Análisis\n"
                    "[1 párrafo sobre cómo se analizaron los datos]\n\n"
                    "## Resultados Principales\n"
                    "### Hallazgos Primarios\n"
                    "[2-3 párrafos sobre los resultados principales con números/datos específicos]\n\n"
                    "### Hallazgos Secundarios\n"
                    "- [Hallazgo 1]\n"
                    "- [Hallazgo 2]\n\n"
                    "## Discusión\n"
                    "[2-3 párrafos interpretando los resultados y comparando con literatura existente]\n\n"
                    "## Implicaciones\n"
                    "### Implicaciones Prácticas\n"
                    "- [Implicación 1]\n"
                    "- [Implicación 2]\n\n"
                    "### Implicaciones Teóricas\n"
                    "- [Implicación 1]\n"
                    "- [Implicación 2]\n\n"
                    "## Limitaciones\n"
                    "- [Limitación 1]\n"
                    "- [Limitación 2]\n\n"
                    "## Futuras Investigaciones\n"
                    "- [Sugerencia 1]\n"
                    "- [Sugerencia 2]\n\n"
                    "Sé exhaustivo y académico. Incluye todos los detalles importantes.\n"
                    "Longitud objetivo: 1,800 palabras.\n\n"
                    "ARTÍCULO:\n{text}"
                )
            },
            "exhaustive": {
                "system": (
                    "Eres un asistente experto en investigación académica. "
                    "Crea resúmenes exhaustivos y comprehensivos que extraigan TODA la información importante de artículos científicos."
                ),
                "user": (
                    "Crea un RESUMEN EXHAUSTIVO (8-10 páginas) del siguiente artículo científico.\n\n"
                    "TU TAREA: Extraer CADA pieza importante de información. Este resumen debe permitir "
                    "que alguien entienda la investigación profundamente sin leer el original.\n\n"
                    "FORMATO REQUERIDO:\n"
                    "# Resumen Exhaustivo\n\n"
                    "## Marco Teórico\n"
                    "[Explicación detallada de teorías, modelos y frameworks utilizados]\n\n"
                    "### Conceptos Clave\n"
                    "- **Concepto 1**: [Definición y relevancia]\n"
                    "- **Concepto 2**: [Definición y relevancia]\n\n"
                    "## Revisión de Literatura\n"
                    "[Descripción comprehensiva de la investigación relacionada citada]\n\n"
                    "### Estudios Previos\n"
                    "[Autor 1 (Año)]: [Hallazgos clave y cómo se relacionan]\n"
                    "[Autor 2 (Año)]: [Hallazgos clave y cómo se relacionan]\n\n"
                    "## Metodología (Comprehensiva)\n"
                    "### Enfoque Epistemológico\n"
                    "[Párrafo sobre el paradigma de investigación]\n\n"
                    "### Diseño del Estudio\n"
                    "[Justificación y descripción detallada]\n\n"
                    "### Muestra\n"
                    "- **Población**: [Descripción]\n"
                    "- **Tamaño de muestra**: [Número y justificación]\n"
                    "- **Método de muestreo**: [Descripción]\n"
                    "- **Criterios de inclusión**: [Lista]\n"
                    "- **Criterios de exclusión**: [Lista]\n\n"
                    "### Instrumentos\n"
                    "[Descripción detallada de cada instrumento de medición]\n\n"
                    "### Procedimientos\n"
                    "[Descripción paso a paso de lo que se hizo]\n\n"
                    "### Consideraciones Éticas\n"
                    "[Descripción de protocolos éticos]\n\n"
                    "### Análisis de Datos\n"
                    "[Descripción comprehensiva de métodos estadísticos/cualitativos]\n\n"
                    "## Resultados (Completos)\n"
                    "### Estadísticas Descriptivas\n"
                    "[Todos los datos descriptivos relevantes]\n\n"
                    "### Hallazgos Principales por Pregunta de Investigación\n"
                    "**PI1**: [Hallazgo con detalles completos]\n"
                    "**PI2**: [Hallazgo con detalles completos]\n\n"
                    "### Resultados Estadísticos\n"
                    "[Todas las pruebas estadísticas significativas con valores]\n\n"
                    "### Tablas y Figuras\n"
                    "[Descripción textual de todas las tablas/figuras]\n\n"
                    "### Hallazgos Inesperados\n"
                    "[Descripción de resultados inesperados]\n\n"
                    "## Discusión (En Profundidad)\n"
                    "### Interpretación de Resultados\n"
                    "[Interpretación exhaustiva]\n\n"
                    "### Comparación con Investigación Previa\n"
                    "[Comparación detallada con literatura]\n\n"
                    "### Explicaciones Alternativas\n"
                    "[Discusión de otras interpretaciones posibles]\n\n"
                    "### Implicaciones Teóricas\n"
                    "[Cómo esto avanza la teoría]\n\n"
                    "### Implicaciones Prácticas\n"
                    "[Aplicaciones prácticas detalladas]\n\n"
                    "## Fortalezas y Limitaciones\n"
                    "### Fortalezas Metodológicas\n"
                    "- [Fortaleza 1]\n"
                    "- [Fortaleza 2]\n\n"
                    "### Limitaciones\n"
                    "- [Limitación 1 con impacto]\n"
                    "- [Limitación 2 con impacto]\n\n"
                    "## Investigación Futura\n"
                    "[Sugerencias detalladas para estudios futuros]\n\n"
                    "## Referencias Clave\n"
                    "[Lista de referencias más importantes citadas]\n\n"
                    "## Apéndice Técnico\n"
                    "- [Ecuaciones importantes]\n"
                    "- [Definiciones técnicas]\n"
                    "- [Terminología especializada]\n\n"
                    "Sé EXTREMADAMENTE exhaustivo. Incluye TODOS los detalles.\n"
                    "Longitud objetivo: 4,000 palabras.\n\n"
                    "ARTÍCULO:\n{text}"
                )
            }
        }

        return prompts.get(level, prompts["detailed"])

    def _summarize_with_groq(self, text: str, level: str = "detailed") -> str:
        """Summarize text using Groq API with level-specific prompts."""
        prompt_config = self._get_prompt_for_level(level)

        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json",
        }

        # Increase max_tokens for longer summaries
        max_tokens_by_level = {
            "executive": 2000,
            "detailed": 6000,
            "exhaustive": 16000,
        }

        payload = {
            "model": self.groq_model,
            "temperature": 0.3,
            "max_tokens": max_tokens_by_level.get(level, 6000),
            "messages": [
                {
                    "role": "system",
                    "content": prompt_config["system"],
                },
                {
                    "role": "user",
                    "content": prompt_config["user"].format(text=text),
                },
            ],
        }

        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=120,  # Increased timeout for longer summaries
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
