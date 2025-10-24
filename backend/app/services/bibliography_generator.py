from typing import List, Dict
from app.models import Article


class BibliographyGenerator:
    @staticmethod
    def generate_apa(article: Article) -> str:
        authors = ", ".join(article.authors) if article.authors else "Unknown"
        year = article.publication_year or "n.d."
        title = article.title or "Unknown"
        journal = article.journal or "Unknown Journal"
        doi = f" https://doi.org/{article.doi}" if article.doi else ""

        return f"{authors} ({year}). {title}. {journal}.{doi}"

    @staticmethod
    def generate_mla(article: Article) -> str:
        authors = ", ".join(article.authors) if article.authors else "Unknown"
        year = article.publication_year or "n.d."
        title = article.title or "Unknown"
        journal = article.journal or "Unknown Journal"
        doi = f" DOI: {article.doi}" if article.doi else ""

        return f"{authors}. \"{title}.\" {journal}, {year}.{doi}"

    @staticmethod
    def generate_chicago(article: Article) -> str:
        authors = ", ".join(article.authors) if article.authors else "Unknown"
        year = article.publication_year or "n.d."
        title = article.title or "Unknown"
        journal = article.journal or "Unknown Journal"
        doi = f" https://doi.org/{article.doi}" if article.doi else ""

        return f"{authors}. \"{title}.\" {journal} ({year}).{doi}"

    @staticmethod
    def generate_bibtex(article: Article) -> str:
        key = article.doi.replace("/", "_") if article.doi else f"article_{article.id}"
        authors = " and ".join(article.authors) if article.authors else "Unknown"
        year = article.publication_year or "n.d."
        title = article.title or "Unknown"
        journal = article.journal or "Unknown Journal"
        doi = f"doi = {{{article.doi}}}," if article.doi else ""

        return f"""@article{{{key},
    author = {{{authors}}},
    year = {{{year}}},
    title = {{{title}}},
    journal = {{{journal}}},
    {doi}
}}"""

    @staticmethod
    def generate_ris(article: Article) -> str:
        authors = "\n".join([f"AU  - {author}" for author in article.authors]) if article.authors else ""
        year = f"PY  - {article.publication_year}\n" if article.publication_year else ""
        title = f"TI  - {article.title}\n" if article.title else ""
        journal = f"JF  - {article.journal}\n" if article.journal else ""
        doi = f"DO  - {article.doi}\n" if article.doi else ""

        return f"""TY  - JOUR
{authors}
{year}{title}{journal}{doi}ER  -"""
