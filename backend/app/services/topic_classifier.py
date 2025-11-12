import re
import unicodedata
from typing import List, Dict, Optional


class TopicClassifier:
    TOPIC_KEYWORDS: Dict[str, List[str]] = {
        "Educación": [
            "educación",
            "educacion",
            "docente",
            "estudiante",
            "escuela",
            "currículo",
            "curriculo",
            "pedagogía",
            "pedagogia",
            "infantil",
            "aprendizaje",
            "learning",
            "teacher",
            "student",
        ],
        "Ciencia": [
            "ciencia",
            "investigación",
            "investigacion",
            "experimento",
            "laboratorio",
            "teoría",
            "teoria",
            "científico",
            "cientifico",
            "science",
        ],
        "Tecnología / IA": [
            "inteligencia artificial",
            "ia",
            "machine learning",
            "aprendizaje automático",
            "aprendizaje automatico",
            "algoritmo",
            "robot",
            "computación",
            "computacion",
            "software",
            "tecnología",
            "tecnologia",
            "ai",
            "deep learning",
            "neural network",
        ],
        "Salud": [
            "salud",
            "medicina",
            "paciente",
            "hospital",
            "clínico",
            "clinico",
            "tratamiento",
            "enfermedad",
            "health",
            "clinical",
        ],
        "Deporte": [
            "deporte",
            "deportes",
            "sport",
            "sports",
            "atleta",
            "athlete",
            "entrenamiento",
            "training",
            "rendimiento",
            "futbol",
            "fútbol",
            "soccer",
            "basketball",
            "tenis",
            "tennis",
            "ejercicio",
            "competencia",
            "match",
            "partido",
        ],
        "Política": [
            "política",
            "politica",
            "gobierno",
            "elección",
            "eleccion",
            "democracia",
            "campaña",
            "public policy",
            "política pública",
            "politica publica",
            "policy",
            "election",
        ],
        "Economía": [
            "economía",
            "economia",
            "finanzas",
            "mercado",
            "inversión",
            "inversion",
            "pib",
            "desarrollo económico",
            "desarrollo economico",
            "empresa",
            "economy",
            "finance",
        ],
        "Medio Ambiente": [
            "medio ambiente",
            "sostenibilidad",
            "clima",
            "ecología",
            "ecologia",
            "emisiones",
            "cambio climático",
            "cambio climatico",
            "energía renovable",
            "energia renovable",
            "environment",
            "sustainability",
        ],
        "Ciencias Sociales": [
            "sociedad",
            "cultural",
            "psicología",
            "psicologia",
            "sociología",
            "sociologia",
            "comportamiento",
            "antropología",
            "antropologia",
            "social",
        ],
    }

    DEFAULT_TOPIC = "General"

    @staticmethod
    def _normalize(text: str) -> str:
        text = text.lower()
        text = unicodedata.normalize('NFD', text)
        text = ''.join(ch for ch in text if unicodedata.category(ch) != 'Mn')
        return text

    def detect_topics(
        self,
        title: str = "",
        abstract: str = "",
        keywords: List[str] = None,
        extra_text: Optional[str] = None,
        max_topics: int = 3,
    ) -> List[str]:
        keywords = keywords or []
        # Weighted text: title > keywords > abstract > extra_text
        parts = [
            (title or "", 3.0),
            (" ".join(keywords), 2.0),
            (abstract or "", 1.5),
            (extra_text or "", 1.0),
        ]
        # Build a normalized bag-of-words string with weights (repeat proportional to weight)
        norm_parts = []
        for p, w in parts:
            if p:
                norm = self._normalize(p)
                # crude weighting: repeat segments
                norm_parts.append((norm + ' ') * int(w))
        text_lower = ' '.join(norm_parts)

        scores = []
        for topic, topic_keywords in self.TOPIC_KEYWORDS.items():
            score = 0.0
            for kw in topic_keywords:
                pattern = re.escape(self._normalize(kw))
                matches = re.findall(pattern, text_lower)
                if matches:
                    score += len(matches)
            normalized = score / max(1, len(topic_keywords))
            if normalized > 0:
                scores.append((topic, normalized))

        if not scores:
            return [self.DEFAULT_TOPIC]

        scores.sort(key=lambda item: item[1], reverse=True)
        return [topic for topic, _ in scores[:max_topics]]

    @classmethod
    def default_topics(cls) -> List[str]:
        return list(cls.TOPIC_KEYWORDS.keys()) + [cls.DEFAULT_TOPIC]
