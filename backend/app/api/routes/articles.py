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
from app.core.schemas import ArticleResponse, ArticleCreate, ArticleUpdate
from app.services.metadata_extractor import MetadataExtractor
from app.services.classifier import ArticleClassifier
from app.services.bibliography_generator import BibliographyGenerator
from app.models import User, Article, Category
import logging

router = APIRouter(prefix="/api/articles", tags=["articles"])
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"


class UrlUpload(BaseModel):
    url: HttpUrl
    category_id: Optional[int] = None


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
        if file_extension.lower() == "pdf":
            try:
                metadata = MetadataExtractor.extract_from_pdf(str(file_path))
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

        db.add(article)
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
    soup = BeautifulSoup(html_content, 'html.parser')
    
    pdf_patterns = [
        ('a', {'href': lambda x: x and '.pdf' in x.lower()}),
        ('a', {'class': lambda x: x and 'download' in ' '.join(x).lower()}),
        ('a', {'title': lambda x: x and 'pdf' in x.lower()}),
        ('meta', {'name': 'citation_pdf_url'}),
        ('link', {'rel': 'alternate', 'type': 'application/pdf'}),
    ]
    
    for tag, attrs in pdf_patterns:
        element = soup.find(tag, attrs)
        if element:
            if tag == 'meta':
                pdf_url = element.get('content')
            elif tag == 'link':
                pdf_url = element.get('href')
            else:
                pdf_url = element.get('href')
            
            if pdf_url:
                if not pdf_url.startswith('http'):
                    from urllib.parse import urljoin
                    pdf_url = urljoin(base_url, pdf_url)
                return pdf_url
    
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
        if file_extension == 'pdf':
            try:
                metadata = MetadataExtractor.extract_from_pdf(str(file_path))
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

        db.add(article)
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
    db: Session = Depends(get_db),
):
    query = db.query(Article).filter(Article.status == "active")

    if category_id:
        query = query.filter(Article.category_id == category_id)

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
