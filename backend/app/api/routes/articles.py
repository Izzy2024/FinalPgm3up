from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
import os
import shutil
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.schemas import (
    ArticleResponse,
    ArticleCreate,
    ArticleUpdate,
    BatchSummaryRequest,
    BatchSummaryResponse,
    SummaryResult,
    MultiDocumentSummaryRequest,
    MultiDocumentSummaryResponse,
)
from app.services.metadata_extractor import MetadataExtractor
from app.services.classifier import ArticleClassifier
from app.services.bibliography_generator import BibliographyGenerator
from app.services.summarizer import ArticleSummarizer
from app.services.topic_classifier import TopicClassifier
from app.services.multi_document_summarizer import MultiDocumentSummarizer
from app.models import User, Article, Category, UserLibrary
from app.core.config import get_settings
import logging

router = APIRouter(prefix="/api/articles", tags=["articles"])
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
settings = get_settings()
topic_classifier = TopicClassifier()


class UrlUpload(BaseModel):
    url: HttpUrl
    category_id: Optional[int] = None


def _assign_topics(article: Article, extra_text: str = ""):
    keywords = article.keywords or []
    abstract = article.abstract or ""
    detected = topic_classifier.detect_topics(
        title=article.title or "",
        abstract=abstract,
        keywords=keywords,
        extra_text=extra_text or "",
    )
    article.auto_topics = detected


def _ensure_user_library_entry(db: Session, user_id: int, article_id: int):
    existing = (
        db.query(UserLibrary)
        .filter(UserLibrary.user_id == user_id, UserLibrary.article_id == article_id)
        .first()
    )
    if not existing:
        db.add(UserLibrary(user_id=user_id, article_id=article_id, status="unread"))


@router.post("/upload", response_model=ArticleResponse)
async def upload_article(
    file: UploadFile = File(...),
    category_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        file_extension = file.filename.split(".")[-1]
        if file_extension.lower() not in ["pdf", "txt"]:
            raise HTTPException(status_code=400, detail="Only PDF and TXT files allowed")

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_name = f"{current_user.id}_{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / file_name

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"File saved to: {file_path}")

        metadata = {}
        text_excerpt = ""
        if file_extension.lower() == "pdf":
            try:
                metadata = MetadataExtractor.extract_from_pdf(str(file_path))
                text_excerpt = metadata.get("text_excerpt") or ""
            except Exception as e:
                logger.error(f"Error extracting PDF metadata: {e}")
                metadata = {}

        file_hash = MetadataExtractor.calculate_file_hash(str(file_path))
        file_size = os.path.getsize(file_path)

        existing_article = db.query(Article).filter(
            Article.file_hash == file_hash
        ).first()
        if existing_article:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="File already uploaded")

        # Ensure title is never None
        title = metadata.get("title") or file.filename or "Untitled Article"
        if not title.strip():
            title = "Untitled Article"

        article = Article(
            title=title,
            authors=metadata.get("authors", []),
            abstract=metadata.get("abstract"),
            keywords=metadata.get("keywords", []),
            publication_year=metadata.get("publication_year"),
            journal=metadata.get("journal"),
            doi=metadata.get("doi"),
            file_path=str(file_path),
            file_size=file_size,
            file_hash=file_hash,
            category_id=category_id,
            uploaded_by=current_user.id,
            status="active",
        )

        _assign_topics(article, extra_text=text_excerpt)

        db.add(article)
        db.flush()
        _ensure_user_library_entry(db, current_user.id, article.id)
        db.commit()
        db.refresh(article)
        
        logger.info(f"Article created with ID: {article.id}")
        return article

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading article: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


def extract_pdf_url_from_html(html_content: str, base_url: str) -> Optional[str]:
    """
    Enhanced PDF extraction supporting Google Scholar, ResearchGate,
    Academia.edu, and other academic platforms.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    from urllib.parse import urljoin, urlparse, parse_qs

    # Google Scholar specific patterns
    if 'scholar.google' in base_url:
        # Look for PDF links in Google Scholar results
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            # Google Scholar often has [PDF] links
            if link.text.strip().upper() == '[PDF]' or 'PDF' in link.text:
                pdf_url = urljoin(base_url, href)
                return pdf_url

        # Check for gs_ggsW class (Google Scholar's PDF viewer)
        gs_link = soup.find('div', class_='gs_ggsW')
        if gs_link:
            pdf_link = gs_link.find('a', href=True)
            if pdf_link:
                return urljoin(base_url, pdf_link['href'])

    # ResearchGate specific patterns
    if 'researchgate.net' in base_url:
        # Look for download button
        download_link = soup.find('a', {'data-test-id': 'work-download-button'})
        if download_link and download_link.get('href'):
            return urljoin(base_url, download_link['href'])

    # Academia.edu specific patterns
    if 'academia.edu' in base_url:
        download_link = soup.find('a', class_=lambda x: x and 'download' in x.lower() if x else False)
        if download_link and download_link.get('href'):
            return urljoin(base_url, download_link['href'])

    # ArXiv specific patterns
    if 'arxiv.org' in base_url:
        # Convert abstract URL to PDF URL
        parsed = urlparse(base_url)
        if '/abs/' in parsed.path:
            pdf_path = parsed.path.replace('/abs/', '/pdf/') + '.pdf'
            return f"{parsed.scheme}://{parsed.netloc}{pdf_path}"

    # General PDF extraction patterns (ordered by reliability)
    pdf_patterns = [
        # Meta tags (most reliable)
        ('meta', {'name': 'citation_pdf_url'}),
        ('meta', {'property': 'og:url', 'content': lambda x: x and '.pdf' in x.lower()}),

        # Link tags
        ('link', {'rel': 'alternate', 'type': 'application/pdf'}),

        # Buttons and download links (common in academic sites)
        ('a', {'class': lambda x: x and any(c in ' '.join(x).lower() for c in ['download-pdf', 'pdf-download', 'download-button']) if x else False}),
        ('a', {'id': lambda x: x and 'pdf' in x.lower() if x else False}),
        ('button', {'class': lambda x: x and 'pdf' in ' '.join(x).lower() if x else False}),

        # Direct PDF links
        ('a', {'href': lambda x: x and x.lower().endswith('.pdf')}),
        ('a', {'href': lambda x: x and '/pdf/' in x.lower()}),

        # Text-based detection
        ('a', {'title': lambda x: x and 'pdf' in x.lower() if x else False}),
        ('a', {'class': lambda x: x and 'download' in ' '.join(x).lower() if x else False}),
    ]

    for tag, attrs in pdf_patterns:
        element = soup.find(tag, attrs)
        if element:
            if tag == 'meta':
                pdf_url = element.get('content')
            elif tag == 'link':
                pdf_url = element.get('href')
            elif tag == 'button':
                # For buttons, look for onclick or data attributes
                pdf_url = element.get('data-url') or element.get('data-href')
                if not pdf_url:
                    continue
            else:
                pdf_url = element.get('href')

            if pdf_url:
                # Clean and normalize URL
                if not pdf_url.startswith('http'):
                    pdf_url = urljoin(base_url, pdf_url)
                return pdf_url

    # Last resort: look for any link containing "pdf" in visible text
    for link in soup.find_all('a', href=True):
        text = link.get_text().lower()
        if 'download' in text and 'pdf' in text:
            href = link['href']
            if not href.startswith('http'):
                href = urljoin(base_url, href)
            return href

    return None


@router.post("/upload-url", response_model=ArticleResponse)
async def upload_article_from_url(
    data: UrlUpload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        url_str = str(data.url)
        logger.info(f"Downloading from URL: {url_str}")

        response = requests.get(url_str, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; SIGRAA/1.0)'
        })
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', '').lower()
        
        if 'text/html' in content_type:
            logger.info("HTML page detected, attempting to extract PDF URL")
            pdf_url = extract_pdf_url_from_html(response.text, url_str)
            
            if pdf_url:
                logger.info(f"Found PDF URL: {pdf_url}")
                response = requests.get(pdf_url, timeout=30, headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; SIGRAA/1.0)'
                })
                response.raise_for_status()
                content_type = response.headers.get('Content-Type', '').lower()
            else:
                raise HTTPException(
                    status_code=400, 
                    detail="Could not find a PDF download link on this page. Please provide a direct PDF URL."
                )
        
        if 'pdf' in content_type:
            file_extension = 'pdf'
        elif 'text/plain' in content_type:
            file_extension = 'txt'
        else:
            file_extension = 'pdf'

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        url_filename = url_str.split('/')[-1].split('?')[0] or 'article'
        file_name = f"{current_user.id}_{timestamp}_{url_filename}.{file_extension}"
        file_path = UPLOAD_DIR / file_name

        with open(file_path, 'wb') as f:
            f.write(response.content)

        logger.info(f"File downloaded to: {file_path}")

        metadata = {}
        text_excerpt = ""
        if file_extension == 'pdf':
            try:
                metadata = MetadataExtractor.extract_from_pdf(str(file_path))
                text_excerpt = metadata.get("text_excerpt") or ""
            except Exception as e:
                logger.error(f"Error extracting PDF metadata: {e}")

        file_hash = MetadataExtractor.calculate_file_hash(str(file_path))
        file_size = os.path.getsize(file_path)

        existing_article = db.query(Article).filter(
            Article.file_hash == file_hash
        ).first()
        if existing_article:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Article already exists in database")

        # Ensure title is never None
        title = metadata.get("title") or url_filename or "Untitled Article"
        if not title.strip():
            title = "Untitled Article"

        article = Article(
            title=title,
            authors=metadata.get("authors", []),
            abstract=metadata.get("abstract"),
            keywords=metadata.get("keywords", []),
            publication_year=metadata.get("publication_year"),
            journal=metadata.get("journal"),
            doi=metadata.get("doi"),
            file_path=str(file_path),
            file_size=file_size,
            file_hash=file_hash,
            category_id=data.category_id,
            uploaded_by=current_user.id,
            status="active",
        )

        _assign_topics(article, extra_text=text_excerpt)

        db.add(article)
        db.flush()
        _ensure_user_library_entry(db, current_user.id, article.id)
        db.commit()
        db.refresh(article)
        
        logger.info(f"Article created from URL with ID: {article.id}")
        return article

    except requests.RequestException as e:
        logger.error(f"Error downloading from URL: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to download from URL: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading from URL: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing URL: {str(e)}")


@router.get("/", response_model=List[ArticleResponse])
def list_articles(
    skip: int = 0,
    limit: int = 10,
    category_id: int = None,
    keyword: Optional[str] = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List articles with advanced filtering options:
    - category_id: Filter by category
    - keyword: Search in title, abstract, keywords, and authors
    - start_year/end_year: Filter by publication year range
    - start_date/end_date: Filter by upload date range (format: YYYY-MM-DD)
    """
    query = db.query(Article).filter(Article.status == "active")

    # Category filter
    if category_id:
        query = query.filter(Article.category_id == category_id)

    # Keyword search (searches in title, abstract, keywords array, and authors array)
    if keyword:
        search_pattern = f"%{keyword}%"
        query = query.filter(
            (Article.title.ilike(search_pattern)) |
            (Article.abstract.ilike(search_pattern)) |
            (Article.keywords.any(keyword)) |
            (Article.authors.any(keyword))
        )

    # Publication year range filter
    if start_year:
        query = query.filter(Article.publication_year >= start_year)
    if end_year:
        query = query.filter(Article.publication_year <= end_year)

    # Upload date range filter
    if start_date:
        try:
            start_datetime = datetime.fromisoformat(start_date)
            query = query.filter(Article.created_at >= start_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")

    if end_date:
        try:
            end_datetime = datetime.fromisoformat(end_date)
            # Add one day to include the entire end date
            from datetime import timedelta
            end_datetime = end_datetime + timedelta(days=1)
            query = query.filter(Article.created_at < end_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")

    # Order by created_at descending (newest first)
    query = query.order_by(Article.created_at.desc())

    articles = query.offset(skip).limit(limit).all()
    return articles


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article(
    article_id: int,
    article_update: ArticleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if article.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = article_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(article, field, value)

    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@router.delete("/{article_id}")
def delete_article(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if article.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if os.path.exists(article.file_path):
        os.remove(article.file_path)

    db.delete(article)
    db.commit()
    return {"message": "Article deleted"}


@router.post("/summaries/batch", response_model=BatchSummaryResponse)
def summarize_articles(
    payload: BatchSummaryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not payload.article_ids:
        raise HTTPException(status_code=400, detail="article_ids cannot be empty.")
    if payload.max_sentences <= 0:
        raise HTTPException(status_code=400, detail="max_sentences must be positive.")
    if payload.combined_max_sentences is not None and payload.combined_max_sentences <= 0:
        raise HTTPException(status_code=400, detail="combined_max_sentences must be positive.")

    summarizer = ArticleSummarizer(settings.groq_api_key)
    results: List[SummaryResult] = []
    combined_sources: List[str] = []

    for article_id in payload.article_ids:
        article = db.query(Article).filter(Article.id == article_id, Article.status == "active").first()
        if not article:
            results.append(
                SummaryResult(
                    article_id=article_id,
                    success=False,
                    error="Article not found.",
                )
            )
            continue

        try:
            # Get article text with appropriate max_pages for the level
            config = summarizer.level_config.get(payload.level, summarizer.level_config["detailed"])
            article_text = summarizer.get_article_text(article, max_pages=config["max_pages"])
            if not article_text:
                raise ValueError("Article has no extractable text to summarize.")

            summary, method_used = summarizer.summarize_text(
                article_text,
                method=payload.method,
                max_sentences=config["max_sentences"],
                level=payload.level,
            )

            results.append(
                SummaryResult(
                    article_id=article.id,
                    title=article.title,
                    success=True,
                    summary=summary,
                    method=method_used,
                )
            )
            combined_sources.append(article_text)
        except Exception as exc:
            logger.error("Failed to summarize article %s: %s", article.id, exc)
            results.append(
                SummaryResult(
                    article_id=article.id,
                    title=article.title,
                    success=False,
                    error=str(exc),
                )
            )

    combined_summary = None
    combined_method = None
    if payload.combined and combined_sources:
        try:
            config = summarizer.level_config.get(payload.level, summarizer.level_config["detailed"])
            combined_summary, combined_method = summarizer.summarize_text(
                " ".join(combined_sources),
                method=payload.method,
                max_sentences=payload.combined_max_sentences or config["max_sentences"],
                level=payload.level,
            )
        except Exception as exc:
            logger.warning("Failed to generate combined summary: %s", exc)

    return BatchSummaryResponse(
        results=results,
        combined_summary=combined_summary,
        combined_method=combined_method,
    )


@router.get("/{article_id}/bibliography/{format}")
def get_article_bibliography(
    article_id: int,
    format: str = "apa",
    db: Session = Depends(get_db),
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    format_lower = format.lower()
    if format_lower == "apa":
        bibliography = BibliographyGenerator.generate_apa(article)
    elif format_lower == "mla":
        bibliography = BibliographyGenerator.generate_mla(article)
    elif format_lower == "chicago":
        bibliography = BibliographyGenerator.generate_chicago(article)
    elif format_lower == "bibtex":
        bibliography = BibliographyGenerator.generate_bibtex(article)
    elif format_lower == "ris":
        bibliography = BibliographyGenerator.generate_ris(article)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
    
    return {
        "article_id": article.id,
        "title": article.title,
        "format": format_lower,
        "bibliography": bibliography
    }


@router.get("/{article_id}/classify")
def classify_article(
    article_id: int,
    db: Session = Depends(get_db),
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    classifier = ArticleClassifier()
    scores = classifier.classify_by_keywords(
        article.title or "",
        article.abstract or "",
        article.keywords or []
    )

    top_category = max(scores, key=scores.get) if scores else None

    return {
        "article_id": article.id,
        "title": article.title,
        "suggested_category": top_category,
        "scores": scores
    }


@router.post("/summaries/multi-document", response_model=MultiDocumentSummaryResponse)
def summarize_multiple_documents(
    payload: MultiDocumentSummaryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate synthesis, comparison, or gap analysis across multiple documents.

    Modes:
    - synthesis: Synthesizes common themes and findings
    - comparison: Compares and contrasts approaches and results
    - gaps: Identifies research gaps and future opportunities
    """
    if not payload.article_ids:
        raise HTTPException(status_code=400, detail="article_ids cannot be empty.")

    if len(payload.article_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="Multi-document analysis requires at least 2 articles."
        )

    if len(payload.article_ids) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 articles allowed for multi-document analysis."
        )

    # Fetch articles
    articles = []
    for article_id in payload.article_ids:
        article = db.query(Article).filter(
            Article.id == article_id,
            Article.status == "active"
        ).first()
        if not article:
            raise HTTPException(
                status_code=404,
                detail=f"Article {article_id} not found or inactive."
            )
        articles.append(article)

    # Generate individual summaries first
    summarizer = ArticleSummarizer(settings.groq_api_key)
    individual_summaries = []

    logger.info(f"Generating individual summaries for {len(articles)} articles")
    for article in articles:
        try:
            summary, _ = summarizer.summarize_article(
                article,
                method="groq",
                level="detailed",  # Use detailed for multi-doc analysis
            )
            individual_summaries.append(summary)
        except Exception as e:
            logger.error(f"Failed to summarize article {article.id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to summarize article {article.id}: {str(e)}"
            )

    # Generate multi-document analysis
    logger.info(f"Generating {payload.mode} analysis for {len(articles)} articles")
    multi_summarizer = MultiDocumentSummarizer(settings.groq_api_key)

    try:
        final_summary = multi_summarizer.summarize_multiple(
            articles=articles,
            individual_summaries=individual_summaries,
            mode=payload.mode,
            level=payload.level,
        )
    except Exception as e:
        logger.error(f"Multi-document summarization failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Multi-document analysis failed: {str(e)}"
        )

    return MultiDocumentSummaryResponse(
        mode=payload.mode,
        level=payload.level,
        article_count=len(articles),
        summary=final_summary,
        method="groq_multi",
    )
