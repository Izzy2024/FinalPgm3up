from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.schemas import ArticleResponse, ArticleCreate, ArticleUpdate
from app.services.metadata_extractor import MetadataExtractor
from app.models import User, Article, Category

router = APIRouter(prefix="/api/articles", tags=["articles"])

UPLOAD_DIR = "data/uploads"


@router.post("/upload", response_model=ArticleResponse)
async def upload_article(
    file: UploadFile = File(...),
    category_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    file_extension = file.filename.split(".")[-1]
    if file_extension.lower() not in ["pdf", "txt"]:
        raise HTTPException(status_code=400, detail="Only PDF and TXT files allowed")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_name = f"{current_user.id}_{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    metadata = MetadataExtractor.extract_from_pdf(file_path) if file_extension.lower() == "pdf" else {}
    file_hash = MetadataExtractor.calculate_file_hash(file_path)
    file_size = os.path.getsize(file_path)

    existing_article = db.query(Article).filter(
        Article.file_hash == file_hash
    ).first()
    if existing_article:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="File already uploaded")

    article = Article(
        title=metadata.get("title", file.filename),
        authors=metadata.get("authors", []),
        abstract=metadata.get("abstract"),
        keywords=metadata.get("keywords", []),
        publication_year=metadata.get("publication_year"),
        journal=metadata.get("journal"),
        doi=metadata.get("doi"),
        file_path=file_path,
        file_size=file_size,
        file_hash=file_hash,
        category_id=category_id,
        uploaded_by=current_user.id,
        status="active",
    )

    db.add(article)
    db.commit()
    db.refresh(article)
    return article


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
