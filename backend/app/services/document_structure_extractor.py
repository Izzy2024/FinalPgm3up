"""
DocumentStructureExtractor - Identifica y extrae secciones de documentos académicos.

Este módulo detecta automáticamente la estructura de artículos científicos,
identificando secciones como Abstract, Introduction, Methodology, Results, etc.
"""

import re
import unicodedata
from typing import Dict, List, Tuple, Optional
import pdfplumber
import logging

logger = logging.getLogger(__name__)


class DocumentStructureExtractor:
    """
    Extrae la estructura de documentos académicos identificando secciones.

    Soporta tanto artículos en inglés como en español.
    """

    # Patrones de secciones en orden de aparición típica
    SECTION_PATTERNS = {
        'abstract': [
            r'^\s*abstract\s*$',
            r'^\s*resumen\s*$',
            r'^\s*summary\s*$',
        ],
        'introduction': [
            r'^\s*(?:1\.?\s*)?introduction\s*$',
            r'^\s*(?:1\.?\s*)?introducción\s*$',
            r'^\s*(?:1\.?\s*)?introduccion\s*$',
            r'^\s*background\s*$',
        ],
        'literature_review': [
            r'^\s*(?:\d+\.?\s*)?literature\s+review\s*$',
            r'^\s*(?:\d+\.?\s*)?related\s+work\s*$',
            r'^\s*(?:\d+\.?\s*)?estado\s+del\s+arte\s*$',
            r'^\s*(?:\d+\.?\s*)?marco\s+teórico\s*$',
            r'^\s*(?:\d+\.?\s*)?marco\s+teorico\s*$',
            r'^\s*(?:\d+\.?\s*)?revisión\s+de\s+literatura\s*$',
            r'^\s*(?:\d+\.?\s*)?revision\s+de\s+literatura\s*$',
        ],
        'methodology': [
            r'^\s*(?:\d+\.?\s*)?methodology\s*$',
            r'^\s*(?:\d+\.?\s*)?methods\s*$',
            r'^\s*(?:\d+\.?\s*)?metodología\s*$',
            r'^\s*(?:\d+\.?\s*)?metodologia\s*$',
            r'^\s*(?:\d+\.?\s*)?métodos\s*$',
            r'^\s*(?:\d+\.?\s*)?metodos\s*$',
            r'^\s*(?:\d+\.?\s*)?materials\s+and\s+methods\s*$',
        ],
        'results': [
            r'^\s*(?:\d+\.?\s*)?results\s*$',
            r'^\s*(?:\d+\.?\s*)?resultados\s*$',
            r'^\s*(?:\d+\.?\s*)?findings\s*$',
            r'^\s*(?:\d+\.?\s*)?hallazgos\s*$',
        ],
        'discussion': [
            r'^\s*(?:\d+\.?\s*)?discussion\s*$',
            r'^\s*(?:\d+\.?\s*)?discusión\s*$',
            r'^\s*(?:\d+\.?\s*)?discusion\s*$',
            r'^\s*(?:\d+\.?\s*)?results\s+and\s+discussion\s*$',
            r'^\s*(?:\d+\.?\s*)?resultados\s+y\s+discusión\s*$',
        ],
        'conclusions': [
            r'^\s*(?:\d+\.?\s*)?conclusions?\s*$',
            r'^\s*(?:\d+\.?\s*)?conclusiones\s*$',
            r'^\s*(?:\d+\.?\s*)?concluding\s+remarks\s*$',
        ],
        'references': [
            r'^\s*references\s*$',
            r'^\s*bibliography\s*$',
            r'^\s*referencias\s*$',
            r'^\s*bibliografía\s*$',
            r'^\s*bibliografia\s*$',
        ],
    }

    def __init__(self):
        # Compilar patrones para mejor performance
        self.compiled_patterns = {}
        for section, patterns in self.SECTION_PATTERNS.items():
            self.compiled_patterns[section] = [
                re.compile(p, re.IGNORECASE | re.UNICODE) for p in patterns
            ]

    def extract_from_pdf(self, pdf_path: str) -> Dict[str, str]:
        """
        Extrae secciones de un PDF académico.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            Diccionario con secciones identificadas: {section_name: content}
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extraer todo el texto con números de página
                pages_text = []
                for i, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if text:
                        pages_text.append((i, text))

                # Identificar límites de secciones
                boundaries = self._identify_section_boundaries(pages_text)

                # Extraer contenido de cada sección
                sections = self._extract_sections_content(pages_text, boundaries)

                return sections

        except Exception as e:
            logger.error(f"Error extracting structure from PDF {pdf_path}: {e}")
            return {}

    def _identify_section_boundaries(
        self, pages_text: List[Tuple[int, str]]
    ) -> Dict[str, Tuple[int, int]]:
        """
        Identifica los límites (inicio, fin) de cada sección.

        Args:
            pages_text: Lista de tuplas (page_number, text)

        Returns:
            Dict con {section_name: (start_line, end_line)}
        """
        # Combinar todo el texto con marcadores de línea
        all_lines = []
        line_to_page = {}
        line_num = 0

        for page_num, text in pages_text:
            lines = text.split('\n')
            for line in lines:
                all_lines.append(line)
                line_to_page[line_num] = page_num
                line_num += 1

        # Encontrar posiciones de cada sección
        section_positions = {}

        for section_name, patterns in self.compiled_patterns.items():
            for i, line in enumerate(all_lines):
                normalized = self._normalize_text(line.strip())

                # Verificar si la línea coincide con algún patrón
                for pattern in patterns:
                    if pattern.match(normalized):
                        # Verificar que sea un título (línea corta, potencialmente seguida de espacio)
                        if len(line.strip()) < 50:
                            section_positions[section_name] = i
                            logger.info(f"Found section '{section_name}' at line {i}: '{line.strip()}'")
                            break

                if section_name in section_positions:
                    break

        # Ordenar secciones por posición
        sorted_sections = sorted(section_positions.items(), key=lambda x: x[1])

        # Calcular límites (inicio, fin) de cada sección
        boundaries = {}
        for i, (section_name, start_line) in enumerate(sorted_sections):
            # El fin de esta sección es el inicio de la siguiente (o el final del documento)
            if i + 1 < len(sorted_sections):
                end_line = sorted_sections[i + 1][1]
            else:
                end_line = len(all_lines)

            boundaries[section_name] = (start_line, end_line)

        return boundaries

    def _extract_sections_content(
        self,
        pages_text: List[Tuple[int, str]],
        boundaries: Dict[str, Tuple[int, int]]
    ) -> Dict[str, str]:
        """
        Extrae el contenido de cada sección según los límites identificados.

        Args:
            pages_text: Lista de tuplas (page_number, text)
            boundaries: Límites de cada sección

        Returns:
            Dict con {section_name: content}
        """
        # Reconstruir todas las líneas
        all_lines = []
        for page_num, text in pages_text:
            all_lines.extend(text.split('\n'))

        sections = {}

        for section_name, (start, end) in boundaries.items():
            # Extraer líneas de esta sección (saltando el título)
            section_lines = all_lines[start + 1:end]

            # Limpiar y unir
            content = '\n'.join(line.strip() for line in section_lines if line.strip())

            # Solo agregar si tiene contenido sustancial
            if len(content) > 100:  # Al menos 100 caracteres
                sections[section_name] = content

        return sections

    def _normalize_text(self, text: str) -> str:
        """
        Normaliza texto para comparación (minúsculas, sin acentos).

        Args:
            text: Texto a normalizar

        Returns:
            Texto normalizado
        """
        # Convertir a minúsculas
        text = text.lower()

        # Remover acentos
        text = unicodedata.normalize('NFD', text)
        text = ''.join(ch for ch in text if unicodedata.category(ch) != 'Mn')

        return text

    def get_section_summary(self, sections: Dict[str, str]) -> str:
        """
        Genera un resumen de las secciones encontradas.

        Args:
            sections: Diccionario con secciones extraídas

        Returns:
            String con resumen de secciones
        """
        summary_lines = ["Document Structure Analysis:", ""]

        if not sections:
            summary_lines.append("No structured sections detected.")
            return '\n'.join(summary_lines)

        for section_name, content in sections.items():
            word_count = len(content.split())
            char_count = len(content)
            summary_lines.append(
                f"✓ {section_name.upper()}: {word_count} words, {char_count} characters"
            )

        total_words = sum(len(content.split()) for content in sections.values())
        summary_lines.append("")
        summary_lines.append(f"Total: {len(sections)} sections, {total_words} words")

        return '\n'.join(summary_lines)


# Función auxiliar para uso rápido
def extract_document_structure(pdf_path: str) -> Dict[str, str]:
    """
    Función de conveniencia para extraer estructura de un documento.

    Args:
        pdf_path: Ruta al PDF

    Returns:
        Diccionario con secciones extraídas
    """
    extractor = DocumentStructureExtractor()
    return extractor.extract_from_pdf(pdf_path)
