import PyPDF2
import pdfplumber
from typing import Dict, List, Optional
import hashlib


class MetadataExtractor:
    @staticmethod
    def extract_from_pdf(file_path: str) -> Dict:
        metadata = {
            "title": None,
            "authors": [],
            "abstract": None,
            "keywords": [],
            "publication_year": None,
            "journal": None,
            "doi": None,
        }

        try:
            with pdfplumber.open(file_path) as pdf:
                if pdf.metadata:
                    metadata["title"] = pdf.metadata.get("Title")
                    metadata["authors"] = pdf.metadata.get("Author", "").split(",")

                if len(pdf.pages) > 0:
                    first_page_text = pdf.pages[0].extract_text()
                    if first_page_text:
                        lines = first_page_text.split("\n")[:20]
                        if not metadata["title"] and len(lines) > 0:
                            metadata["title"] = lines[0][:500]

                full_text = "\n".join(
                    [page.extract_text() for page in pdf.pages[:3]]
                )
                if "Abstract" in full_text or "ABSTRACT" in full_text:
                    abstract_start = full_text.lower().find("abstract")
                    if abstract_start != -1:
                        abstract_end = min(
                            abstract_start + 800, len(full_text)
                        )
                        metadata["abstract"] = full_text[abstract_start:abstract_end]

        except Exception as e:
            print(f"Error extracting PDF metadata: {e}")

        return metadata

    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
