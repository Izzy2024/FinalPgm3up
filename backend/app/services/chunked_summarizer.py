"""
ChunkedSummarizer - Procesa documentos largos usando Map-Reduce.

Este módulo divide documentos extensos en chunks manejables, resume cada uno,
y luego combina los resúmenes en un resultado coherente.
"""

import logging
import math
from typing import List, Tuple, Dict, Optional
import requests

logger = logging.getLogger(__name__)


class ChunkedSummarizer:
    """
    Resumidor que procesa documentos largos usando estrategia Map-Reduce.

    Map: Resume cada chunk individualmente
    Reduce: Combina resúmenes parciales en uno coherente
    """

    def __init__(
        self,
        groq_api_key: str,
        groq_model: str = "llama-3.3-70b-versatile",
        chunk_size_chars: int = 8000,
        overlap_chars: int = 800,
    ):
        """
        Inicializa el ChunkedSummarizer.

        Args:
            groq_api_key: API key de Groq
            groq_model: Modelo a usar
            chunk_size_chars: Tamaño de cada chunk en caracteres
            overlap_chars: Overlap entre chunks para mantener contexto
        """
        self.groq_api_key = groq_api_key
        self.groq_model = groq_model
        self.chunk_size = chunk_size_chars
        self.overlap = overlap_chars

    def summarize_long_document(
        self,
        text: str,
        level: str = "detailed",
        sections: Optional[Dict[str, str]] = None,
    ) -> Tuple[str, str]:
        """
        Resume un documento largo usando Map-Reduce.

        Args:
            text: Texto completo del documento
            level: Nivel de resumen (executive, detailed, exhaustive)
            sections: Secciones del documento si están disponibles

        Returns:
            Tupla (resumen, método_usado)
        """
        if not text:
            raise ValueError("Text cannot be empty")

        # Si el documento es corto, resumir directamente
        if len(text) < self.chunk_size:
            logger.info("Document is short, summarizing directly")
            return self._summarize_with_groq(text, level, is_final=True), "groq_direct"

        logger.info(f"Document is long ({len(text)} chars), using chunked approach")

        # FASE MAP: Dividir y resumir cada chunk
        chunks = self._create_overlapping_chunks(text)
        logger.info(f"Created {len(chunks)} chunks")

        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            try:
                summary = self._summarize_chunk(
                    chunk,
                    chunk_number=i + 1,
                    total_chunks=len(chunks),
                    level=level,
                )
                chunk_summaries.append(summary)
                logger.info(f"Summarized chunk {i + 1}/{len(chunks)}")
            except Exception as e:
                logger.error(f"Error summarizing chunk {i + 1}: {e}")
                # Continuar con los otros chunks

        if not chunk_summaries:
            raise RuntimeError("Failed to summarize any chunks")

        # FASE REDUCE: Combinar resúmenes parciales
        logger.info("Reducing chunk summaries into final summary")
        final_summary = self._merge_summaries(
            chunk_summaries,
            level=level,
            sections=sections,
        )

        return final_summary, "groq_map_reduce"

    def _create_overlapping_chunks(self, text: str) -> List[str]:
        """
        Divide texto en chunks con overlap.

        Args:
            text: Texto completo

        Returns:
            Lista de chunks
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            # Fin del chunk
            end = start + self.chunk_size

            # Si no es el último chunk, ajustar para no cortar en medio de palabra
            if end < text_length:
                # Buscar el último espacio antes del límite
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Siguiente chunk comienza con overlap
            start = end - self.overlap

        return chunks

    def _summarize_chunk(
        self,
        chunk: str,
        chunk_number: int,
        total_chunks: int,
        level: str,
    ) -> str:
        """
        Resume un chunk individual.

        Args:
            chunk: Texto del chunk
            chunk_number: Número del chunk (1-indexed)
            total_chunks: Total de chunks
            level: Nivel de resumen

        Returns:
            Resumen del chunk
        """
        # Prompt específico para chunks
        system_prompt = (
            "Eres un asistente experto en investigación académica. "
            "Estás resumiendo UNA PARTE de un documento más largo. "
            "Resume este fragmento capturando toda la información importante."
        )

        user_prompt = f"""Resume el siguiente fragmento de un documento académico.

CONTEXTO: Este es el fragmento {chunk_number} de {total_chunks} fragmentos totales.

INSTRUCCIONES:
- Resume este fragmento capturando TODOS los puntos importantes
- Mantén la estructura y organización del contenido
- No agregues conclusiones si este fragmento no las contiene
- Enfócate en los hechos y datos presentes en este fragmento

FRAGMENTO {chunk_number}:
{chunk}

Resume este fragmento de forma completa y estructurada."""

        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.groq_model,
            "temperature": 0.3,
            "max_tokens": 2000,  # Resumen moderado por chunk
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
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"Error calling Groq for chunk {chunk_number}: {e}")
            raise

    def _merge_summaries(
        self,
        summaries: List[str],
        level: str,
        sections: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Combina resúmenes parciales en un resumen final coherente.

        Args:
            summaries: Lista de resúmenes de chunks
            level: Nivel de resumen
            sections: Secciones del documento (opcional)

        Returns:
            Resumen final combinado
        """
        combined_text = "\n\n---\n\n".join(summaries)

        # Prompt para la fase REDUCE
        level_descriptions = {
            "executive": "un resumen ejecutivo de 1 página (~500 palabras)",
            "detailed": "un resumen detallado de 3-4 páginas (~1,800 palabras)",
            "exhaustive": "un resumen exhaustivo de 8-10 páginas (~4,000 palabras)",
        }

        system_prompt = (
            "Eres un asistente experto en investigación académica. "
            "Tu tarea es SINTETIZAR múltiples resúmenes parciales en un resumen final coherente."
        )

        user_prompt = f"""Tienes {len(summaries)} resúmenes parciales de un documento académico.

TU TAREA: Sintetizar estos resúmenes en {level_descriptions.get(level, 'un resumen completo')}.

INSTRUCCIONES CRÍTICAS:
- INTEGRA toda la información de los resúmenes parciales
- Elimina redundancias entre fragmentos
- Mantén la ESTRUCTURA ACADÉMICA apropiada
- Asegura COHERENCIA narrativa
- Preserva TODOS los datos, cifras y hallazgos importantes
- Organiza por secciones lógicas (Introducción, Metodología, Resultados, etc.)

RESÚMENES PARCIALES A SINTETIZAR:

{combined_text}

Sintetiza estos resúmenes en un documento académico coherente y completo."""

        return self._summarize_with_groq(combined_text, level, is_final=True, custom_prompt=user_prompt)

    def _summarize_with_groq(
        self,
        text: str,
        level: str,
        is_final: bool = False,
        custom_prompt: Optional[str] = None,
    ) -> str:
        """
        Llama a Groq para resumir texto.

        Args:
            text: Texto a resumir
            level: Nivel de resumen
            is_final: Si es el resumen final (usa más tokens)
            custom_prompt: Prompt personalizado (opcional)

        Returns:
            Resumen generado
        """
        # Importar prompts del summarizer original
        from app.services.summarizer import ArticleSummarizer

        temp_summarizer = ArticleSummarizer(self.groq_api_key, self.groq_model)
        prompt_config = temp_summarizer._get_prompt_for_level(level)

        system_prompt = prompt_config["system"]
        user_prompt = custom_prompt or prompt_config["user"].format(text=text)

        # Tokens según si es final o intermedio
        max_tokens = {
            "executive": 2000 if is_final else 1000,
            "detailed": 6000 if is_final else 2000,
            "exhaustive": 16000 if is_final else 4000,
        }

        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.groq_model,
            "temperature": 0.3,
            "max_tokens": max_tokens.get(level, 6000),
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
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"Error calling Groq: {e}")
            raise RuntimeError(f"Groq API call failed: {e}")

    def estimate_chunks_needed(self, text_length: int) -> int:
        """
        Estima cuántos chunks se necesitarán.

        Args:
            text_length: Longitud del texto en caracteres

        Returns:
            Número estimado de chunks
        """
        if text_length <= self.chunk_size:
            return 1

        # Calcular considerando overlap
        effective_chunk_size = self.chunk_size - self.overlap
        return math.ceil((text_length - self.overlap) / effective_chunk_size)
