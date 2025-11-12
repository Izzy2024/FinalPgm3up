"""
MultiDocumentSummarizer - Sintetiza y compara múltiples documentos.

Este módulo permite generar resúmenes comparativos, identificar gaps
en la literatura, y sintetizar hallazgos de múltiples artículos.
"""

import logging
from typing import List, Dict, Optional
import requests
from app.models.article import Article

logger = logging.getLogger(__name__)


class MultiDocumentSummarizer:
    """
    Resumidor que trabaja con múltiples documentos simultáneamente.

    Soporta tres modos:
    - synthesis: Sintetiza ideas comunes entre documentos
    - comparison: Compara diferencias y perspectivas
    - gaps: Identifica vacíos en la literatura
    """

    def __init__(
        self,
        groq_api_key: str,
        groq_model: str = "llama-3.3-70b-versatile",
    ):
        """
        Inicializa el MultiDocumentSummarizer.

        Args:
            groq_api_key: API key de Groq
            groq_model: Modelo a usar
        """
        self.groq_api_key = groq_api_key
        self.groq_model = groq_model

    def summarize_multiple(
        self,
        articles: List[Article],
        individual_summaries: List[str],
        mode: str = "synthesis",
        level: str = "detailed",
    ) -> str:
        """
        Genera resumen de múltiples documentos.

        Args:
            articles: Lista de artículos
            individual_summaries: Resúmenes individuales de cada artículo
            mode: Modo de análisis (synthesis, comparison, gaps)
            level: Nivel de detalle

        Returns:
            Resumen multi-documento
        """
        if not articles or not individual_summaries:
            raise ValueError("Need at least one article and summary")

        if len(articles) != len(individual_summaries):
            raise ValueError("Number of articles and summaries must match")

        # Preparar contexto de artículos
        articles_context = self._prepare_articles_context(articles, individual_summaries)

        # Generar resumen según modo
        if mode == "synthesis":
            return self._generate_synthesis(articles_context, level)
        elif mode == "comparison":
            return self._generate_comparison(articles_context, level)
        elif mode == "gaps":
            return self._generate_gaps_analysis(articles_context, level)
        else:
            raise ValueError(f"Unknown mode: {mode}")

    def _prepare_articles_context(
        self,
        articles: List[Article],
        summaries: List[str],
    ) -> str:
        """
        Prepara el contexto de artículos para el prompt.

        Args:
            articles: Lista de artículos
            summaries: Lista de resúmenes

        Returns:
            String con contexto formateado
        """
        context_parts = []

        for i, (article, summary) in enumerate(zip(articles, summaries), start=1):
            authors_str = ", ".join(article.authors[:3]) if article.authors else "Unknown"
            if article.authors and len(article.authors) > 3:
                authors_str += " et al."

            year = article.publication_year or "N/A"

            context_parts.append(f"""
═══════════════════════════════════════════════════
ARTÍCULO {i}
═══════════════════════════════════════════════════

TÍTULO: {article.title}
AUTORES: {authors_str}
AÑO: {year}
JOURNAL: {article.journal or "N/A"}

RESUMEN:
{summary}
""")

        return "\n".join(context_parts)

    def _generate_synthesis(self, articles_context: str, level: str) -> str:
        """
        Genera síntesis de múltiples documentos.

        Args:
            articles_context: Contexto de artículos
            level: Nivel de detalle

        Returns:
            Síntesis generada
        """
        word_targets = {
            "executive": "1,000 palabras",
            "detailed": "2,500 palabras",
            "exhaustive": "5,000 palabras",
        }

        system_prompt = (
            "Eres un experto en revisión de literatura académica. "
            "Tu tarea es SINTETIZAR múltiples estudios en un análisis coherente "
            "que identifica patrones, temas comunes y consenso en el campo."
        )

        user_prompt = f"""Analiza los siguientes artículos de investigación y crea una SÍNTESIS INTEGRADA.

{articles_context}

═══════════════════════════════════════════════════
TU TAREA: SÍNTESIS ACADÉMICA
═══════════════════════════════════════════════════

Crea una síntesis académica completa que integre estos estudios.

ESTRUCTURA REQUERIDA:

# Síntesis de Literatura

## 1. Introducción
[Breve overview del cuerpo de literatura analizado]

## 2. Temas Principales Identificados
### Tema 1: [Nombre del tema]
- Artículos que lo abordan: [Referencias]
- Hallazgos convergentes: [Síntesis]
- Metodologías utilizadas: [Resumen]

### Tema 2: [Nombre del tema]
[Mismo formato]

[Continuar con todos los temas principales]

## 3. Enfoques Metodológicos
- Metodologías cuantitativas: [Resumen de estudios]
- Metodologías cualitativas: [Resumen de estudios]
- Métodos mixtos: [Resumen de estudios]

## 4. Hallazgos Convergentes
[Qué dicen TODOS o la MAYORÍA de los estudios? Sintetiza el consenso]

## 5. Evolución Temporal
[Si hay diferencia de años, ¿cómo ha evolucionado el conocimiento?]

## 6. Marcos Teóricos Utilizados
[Qué teorías y frameworks son comunes en estos estudios?]

## 7. Poblaciones y Contextos Estudiados
[Dónde y con quién se han hecho estos estudios?]

## 8. Conclusiones Integradas
[Qué podemos concluir del cuerpo de literatura en conjunto?]

## 9. Implicaciones
### Implicaciones Teóricas
[Para el desarrollo teórico del campo]

### Implicaciones Prácticas
[Para la práctica profesional]

## 10. Fortalezas del Cuerpo de Literatura
[Qué hacen bien estos estudios colectivamente?]

INSTRUCCIONES CRÍTICAS:
- INTEGRA los hallazgos en narrativas coherentes
- IDENTIFICA patrones y temas transversales
- REFERENCIA artículos específicos al hacer afirmaciones
- Usa lenguaje académico formal
- Target: {word_targets.get(level, '2,500 palabras')}
- Sé exhaustivo y analítico"""

        return self._call_groq(system_prompt, user_prompt, level)

    def _generate_comparison(self, articles_context: str, level: str) -> str:
        """
        Genera análisis comparativo de múltiples documentos.

        Args:
            articles_context: Contexto de artículos
            level: Nivel de detalle

        Returns:
            Comparación generada
        """
        word_targets = {
            "executive": "1,000 palabras",
            "detailed": "2,500 palabras",
            "exhaustive": "5,000 palabras",
        }

        system_prompt = (
            "Eres un experto en análisis comparativo de literatura académica. "
            "Tu tarea es COMPARAR Y CONTRASTAR múltiples estudios, "
            "identificando diferencias, contradicciones y perspectivas diversas."
        )

        user_prompt = f"""Analiza los siguientes artículos y crea un ANÁLISIS COMPARATIVO.

{articles_context}

═══════════════════════════════════════════════════
TU TAREA: ANÁLISIS COMPARATIVO
═══════════════════════════════════════════════════

Crea un análisis que compare y contraste estos estudios sistemáticamente.

ESTRUCTURA REQUERIDA:

# Análisis Comparativo de Literatura

## 1. Overview de los Estudios
[Tabla o descripción general de cada estudio]

## 2. Comparación de Enfoques Metodológicos

### Diseños de Investigación
| Artículo | Diseño | Fortaleza | Limitación |
|----------|---------|-----------|------------|
[Tabla comparativa]

### Muestras y Participantes
- Artículo 1: [Características de muestra]
- Artículo 2: [Características de muestra]
[Análisis de similitudes y diferencias]

### Instrumentos de Medición
[Comparación de instrumentos usados]

## 3. Hallazgos Divergentes

### Tema/Variable 1
- **Artículo A encontró**: [Hallazgo]
- **Artículo B encontró**: [Hallazgo diferente/contradictorio]
- **Artículo C encontró**: [Hallazgo]
- **Análisis de la divergencia**: [Posibles explicaciones]

### Tema/Variable 2
[Mismo formato]

## 4. Diferentes Perspectivas Teóricas
[Cómo difieren los marcos teóricos y qué implica esto?]

## 5. Contextos y Poblaciones
[Comparación de dónde y con quién se realizaron los estudios]

## 6. Calidad Metodológica Comparativa
### Rigor Metodológico
- Artículo más riguroso: [Justificación]
- Consideraciones sobre cada estudio

### Validez y Confiabilidad
[Comparación de validez interna/externa]

## 7. Contribuciones Únicas de Cada Estudio
- Artículo 1 contribuye: [Contribución única]
- Artículo 2 contribuye: [Contribución única]

## 8. Coherencia vs. Contradicción
### Áreas de Consenso
[Dónde coinciden los estudios]

### Áreas de Contradicción
[Dónde difieren o contradicen]
[Posibles explicaciones de contradicciones]

## 9. Evaluación Comparativa
### Cuál estudio es más relevante para:
- Investigación básica: [Justificación]
- Aplicación práctica: [Justificación]
- Desarrollo teórico: [Justificación]

## 10. Síntesis Comparativa Final
[Conclusiones del análisis comparativo]

INSTRUCCIONES CRÍTICAS:
- SÉ ESPECÍFICO al comparar (cita artículos exactos)
- EXPLICA las diferencias (no solo las describas)
- Mantén objetividad académica
- Target: {word_targets.get(level, '2,500 palabras')}"""

        return self._call_groq(system_prompt, user_prompt, level)

    def _generate_gaps_analysis(self, articles_context: str, level: str) -> str:
        """
        Genera análisis de gaps en la literatura.

        Args:
            articles_context: Contexto de artículos
            level: Nivel de detalle

        Returns:
            Análisis de gaps
        """
        word_targets = {
            "executive": "800 palabras",
            "detailed": "2,000 palabras",
            "exhaustive": "4,000 palabras",
        }

        system_prompt = (
            "Eres un experto en análisis de literatura académica. "
            "Tu especialidad es IDENTIFICAR GAPS (vacíos) en la investigación "
            "que representan oportunidades para futuros estudios."
        )

        user_prompt = f"""Analiza los siguientes artículos e IDENTIFICA GAPS en la literatura.

{articles_context}

═══════════════════════════════════════════════════
TU TAREA: ANÁLISIS DE GAPS EN LA LITERATURA
═══════════════════════════════════════════════════

Identifica sistemáticamente qué falta en este cuerpo de literatura.

ESTRUCTURA REQUERIDA:

# Análisis de Gaps en la Literatura

## 1. Resumen del Cuerpo de Literatura Analizado
[Breve descripción de qué cubre esta literatura]

## 2. Lo Que Sabemos (Áreas Cubiertas)
### Temas Bien Investigados
- Tema 1: [Descripción de cobertura]
- Tema 2: [Descripción de cobertura]

### Métodos Bien Establecidos
[Qué metodologías están bien representadas?]

## 3. GAPS METODOLÓGICOS

### Diseños de Investigación No Utilizados
- **Gap**: [Tipo de diseño faltante]
- **Oportunidad**: [Por qué sería valioso]
- **Justificación**: [Cómo llenaría un vacío]

### Métodos de Análisis Ausentes
[Qué técnicas analíticas no se han usado?]

### Combinaciones Metodológicas
[Qué enfoques mixtos podrían ser valiosos?]

## 4. GAPS DE POBLACIÓN Y CONTEXTO

### Poblaciones No Estudiadas
- **Gap**: [Población faltante]
- **Importancia**: [Por qué es importante estudiarla]

### Contextos Geográficos/Culturales
[Dónde NO se ha investigado?]

### Settings No Explorados
[Qué contextos específicos faltan?]

## 5. GAPS TEÓRICOS

### Marcos Teóricos No Aplicados
[Qué teorías podrían ofrecer nuevas perspectivas?]

### Integraciones Teóricas Potenciales
[Qué teorías podrían combinarse?]

## 6. GAPS DE VARIABLES Y FACTORES

### Variables No Consideradas
- Variable 1: [Por qué sería importante]
- Variable 2: [Por qué sería importante]

### Interacciones No Exploradas
[Qué relaciones entre variables no se han estudiado?]

### Mediadores y Moderadores
[Qué factores intermedios no se han investigado?]

## 7. GAPS TEMPORALES

### Períodos No Cubiertos
[Hay períodos históricos sin estudiar?]

### Estudios Longitudinales
[Se necesitan más estudios de seguimiento?]

## 8. GAPS EN OUTCOMES Y MEDICIONES

### Resultados No Medidos
[Qué outcomes importantes no se han considerado?]

### Instrumentos de Medición
[Qué necesita ser medido de nuevas formas?]

## 9. PRIORIZACIÓN DE GAPS

### Gaps Más Críticos (Top 5)
1. **Gap**: [Descripción]
   - **Impacto potencial**: [Alto/Medio/Bajo]
   - **Viabilidad**: [Alta/Media/Baja]
   - **Justificación**: [Por qué es prioridad]

[Continuar con top 5]

## 10. AGENDA DE INVESTIGACIÓN FUTURA

### Preguntas de Investigación Propuestas
**RQ1**: [Pregunta específica para llenar gap]
- **Gap que llena**: [Referencia al gap]
- **Metodología sugerida**: [Breve descripción]

**RQ2**: [Pregunta específica]
[Continuar...]

### Estudios Recomendados
1. **Estudio Propuesto**: [Título descriptivo]
   - **Tipo**: [Experimental/Observacional/etc.]
   - **Población**: [Descripción]
   - **Gap que llena**: [Referencia]

[Continuar con propuestas específicas]

## 11. Implicaciones para el Campo
[Cómo el llenar estos gaps avanzaría el campo?]

INSTRUCCIONES CRÍTICAS:
- SÉ ESPECÍFICO sobre cada gap
- JUSTIFICA por qué es un gap importante
- PROPONE formas concretas de llenarlo
- Prioriza gaps por importancia
- Target: {word_targets.get(level, '2,000 palabras')}"""

        return self._call_groq(system_prompt, user_prompt, level)

    def _call_groq(self, system_prompt: str, user_prompt: str, level: str) -> str:
        """
        Llama a Groq API.

        Args:
            system_prompt: Prompt del sistema
            user_prompt: Prompt del usuario
            level: Nivel de detalle

        Returns:
            Respuesta de Groq
        """
        max_tokens = {
            "executive": 4000,
            "detailed": 8000,
            "exhaustive": 16000,
        }

        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.groq_model,
            "temperature": 0.3,
            "max_tokens": max_tokens.get(level, 8000),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=180,  # 3 minutos para análisis complejos
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"Error calling Groq for multi-document summary: {e}")
            raise RuntimeError(f"Groq API call failed: {e}")
