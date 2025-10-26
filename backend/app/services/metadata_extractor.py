import PyPDF2
import pdfplumber
from typing import Dict, List, Optional
import hashlib
import re


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
                # Try to get metadata from PDF properties
                if pdf.metadata:
                    if pdf.metadata.get("Title"):
                        metadata["title"] = pdf.metadata.get("Title").strip()
                    
                    authors_str = pdf.metadata.get("Author", "")
                    if authors_str:
                        metadata["authors"] = [a.strip() for a in authors_str.split(",") if a.strip()]

                # Extract text from first 3 pages for better metadata extraction
                if len(pdf.pages) > 0:
                    first_page_text = pdf.pages[0].extract_text() or ""
                    
                    # Try to extract title from first page if not in metadata
                    if not metadata["title"] and first_page_text:
                        lines = [line.strip() for line in first_page_text.split("\n") if line.strip()]
                        
                        # Look for title patterns (usually largest text on first page)
                        for i, line in enumerate(lines[:15]):
                            # Skip very short lines or common headers
                            if len(line) > 10 and not line.lower().startswith(('www.', 'http', 'doi:', 'issn')):
                                # Check if line looks like a title (not all caps, reasonable length)
                                if len(line) < 200 and not line.isupper():
                                    metadata["title"] = line
                                    break
                    
                    # Try to extract DOI
                    doi_match = re.search(r'(?:doi:|DOI:)\s*([^\s]+)', first_page_text)
                    if doi_match:
                        metadata["doi"] = doi_match.group(1).strip()
                    else:
                        # Alternative DOI pattern
                        doi_match = re.search(r'10\.\d{4,}/[^\s]+', first_page_text)
                        if doi_match:
                            metadata["doi"] = doi_match.group(0).strip()
                    
                    # Try to extract year
                    year_match = re.search(r'\b(19|20)\d{2}\b', first_page_text)
                    if year_match:
                        metadata["publication_year"] = int(year_match.group(0))

                # Extract abstract from first few pages
                full_text = "\n".join(
                    [page.extract_text() or "" for page in pdf.pages[:3]]
                )
                
                if full_text:
                    # Look for abstract section
                    abstract_patterns = [
                        r'(?:Abstract|ABSTRACT|Resumen|RESUMEN)[:\s]*(.*?)(?=\n\n|\nKeywords|\nPalabras clave|\nIntroduction|\nINTRODUCTION|\n1\.|\nMethods)',
                        r'(?:Abstract|ABSTRACT)[:\s]*(.*?)(?=\n[A-Z][a-z]+:|\n\d+\.)',
                    ]
                    
                    for pattern in abstract_patterns:
                        abstract_match = re.search(pattern, full_text, re.DOTALL | re.IGNORECASE)
                        if abstract_match:
                            abstract_text = abstract_match.group(1).strip()
                            # Clean up the abstract
                            abstract_text = re.sub(r'\s+', ' ', abstract_text)
                            metadata["abstract"] = abstract_text[:1000]  # Limit length
                            break
                    
                    # Look for keywords
                    keywords_patterns = [
                        r'(?:Keywords|KEYWORDS|Palabras clave)[:\s]*(.*?)(?=\n\n|\nIntroduction)',
                        r'(?:Key words)[:\s]*(.*?)(?=\n)',
                    ]
                    
                    for pattern in keywords_patterns:
                        keywords_match = re.search(pattern, full_text, re.DOTALL | re.IGNORECASE)
                        if keywords_match:
                            keywords_text = keywords_match.group(1).strip()
                            # Split by common delimiters
                            keywords_list = re.split(r'[;,]', keywords_text)
                            metadata["keywords"] = [k.strip() for k in keywords_list if k.strip()][:10]
                            break

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
