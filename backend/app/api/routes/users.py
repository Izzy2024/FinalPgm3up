from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.schemas import (
    UserResponse,
    UserUpdate,
    LibraryEntryUpdate,
    UserIndexCreate,
    UserIndexResponse,
)
from app.models import User, Article, UserLibrary, UserIndex
from app.services.topic_classifier import TopicClassifier

router = APIRouter(prefix="/api/users", tags=["users"])
topic_classifier = TopicClassifier()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/profile", response_model=UserResponse)
def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/library/{article_id}")
def add_to_library(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    existing = db.query(UserLibrary).filter(
        UserLibrary.user_id == current_user.id,
        UserLibrary.article_id == article_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Article already in library")

    user_library = UserLibrary(
        user_id=current_user.id,
        article_id=article_id,
        status="unread"
    )
    db.add(user_library)
    db.commit()
    db.refresh(user_library)
    return {"message": "Article added to library", "id": user_library.id}


@router.delete("/library/{article_id}")
def remove_from_library(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_library = db.query(UserLibrary).filter(
        UserLibrary.user_id == current_user.id,
        UserLibrary.article_id == article_id
    ).first()
    if not user_library:
        raise HTTPException(status_code=404, detail="Article not in library")

    db.delete(user_library)
    db.commit()
    return {"message": "Article removed from library"}


def _apply_keyword_filter(query, keywords: List[str]):
    cleaned = [kw.strip() for kw in keywords if kw.strip()]
    if not cleaned:
        return query

    conditions = []
    for keyword in cleaned:
        pattern = f"%{keyword}%"
        conditions.extend(
            [
                Article.title.ilike(pattern),
                func.coalesce(Article.abstract, "").ilike(pattern),
                func.coalesce(func.array_to_string(Article.keywords, " "), "").ilike(pattern),
                func.coalesce(func.array_to_string(Article.auto_topics, " "), "").ilike(pattern),
            ]
        )
    return query.filter(or_(*conditions))


@router.get("/library/")
def get_user_library(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    topic: Optional[str] = None,
    search: Optional[str] = None,
    index_id: Optional[int] = None,
    sort: str = "recent",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        db.query(UserLibrary)
        .join(Article)
        .options(joinedload(UserLibrary.article))
        .filter(UserLibrary.user_id == current_user.id)
    )

    if status and status != "all":
        query = query.filter(UserLibrary.status == status)

    if topic:
        if topic == TopicClassifier.DEFAULT_TOPIC:
            query = query.filter(
                or_(
                    # user override empty or contains 'General'
                    UserLibrary.user_topics.is_(None),
                    func.cardinality(UserLibrary.user_topics) == 0,
                    UserLibrary.user_topics.any(topic),
                    # or article topics empty or contains 'General'
                    Article.auto_topics.is_(None),
                    func.cardinality(Article.auto_topics) == 0,
                    Article.auto_topics.any(topic),
                )
            )
        else:
            query = query.filter(
                or_(
                    UserLibrary.user_topics.any(topic),
                    Article.auto_topics.any(topic),
                )
            )

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                Article.title.ilike(pattern),
                func.coalesce(Article.abstract, "").ilike(pattern),
                func.coalesce(func.array_to_string(Article.authors, " "), "").ilike(pattern),
                func.coalesce(func.array_to_string(Article.keywords, " "), "").ilike(pattern),
            )
        )

    if index_id:
        user_index = (
            db.query(UserIndex)
            .filter(UserIndex.id == index_id, UserIndex.user_id == current_user.id)
            .first()
        )
        if not user_index:
            raise HTTPException(status_code=404, detail="Index not found")
        query = _apply_keyword_filter(query, user_index.keywords or [])

    total = query.count()

    if sort == "title":
        query = query.order_by(Article.title.asc())
    elif sort == "rating":
        query = query.order_by(
            UserLibrary.rating.desc().nullslast(), UserLibrary.added_at.desc()
        )
    else:
        query = query.order_by(UserLibrary.added_at.desc())

    user_libraries = query.offset(skip).limit(limit).all()

    items = []
    for ul in user_libraries:
        article = ul.article
        article_payload = {
            "id": article.id,
            "title": article.title,
            "authors": article.authors,
            "abstract": article.abstract,
            "keywords": article.keywords,
            "publication_year": article.publication_year,
            "journal": article.journal,
            "doi": article.doi,
            "file_path": article.file_path,
            "category_id": article.category_id,
            "status": article.status,
            "created_at": article.created_at,
            "updated_at": article.updated_at,
            "auto_topics": article.auto_topics or [],
        }

        # Prefer user topics if present; else fallback to article.auto_topics
        effective_topics = ul.user_topics if getattr(ul, 'user_topics', None) else (article.auto_topics or [])

        items.append(
            {
                "id": ul.id,
                "article_id": ul.article_id,
                "title": article.title,
                "authors": article.authors,
                "status": ul.status,
                "rating": ul.rating,
                "notes": ul.notes,
                "added_at": ul.added_at,
                "updated_at": ul.updated_at,
                "topics": effective_topics,
                "article": article_payload,
            }
        )

    return {
        "total": total,
        "items": items,
    }


@router.put("/library/{article_id}")
def update_library_entry(
    article_id: int,
    payload: LibraryEntryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_library = db.query(UserLibrary).filter(
        UserLibrary.user_id == current_user.id,
        UserLibrary.article_id == article_id
    ).first()
    if not user_library:
        raise HTTPException(status_code=404, detail="Article not in library")

    if payload.status:
        if payload.status not in {"unread", "reading", "read"}:
            raise HTTPException(status_code=400, detail="Invalid status value")
        user_library.status = payload.status
    if payload.rating is not None:
        if payload.rating < 0 or payload.rating > 5:
            raise HTTPException(status_code=400, detail="Rating must be between 0 and 5")
        user_library.rating = payload.rating
    if payload.notes is not None:
        user_library.notes = payload.notes
    if payload.topics is not None:
        # Normalize topics to known defaults when possible
        requested = [t.strip() for t in payload.topics if t and t.strip()]
        # Allow any string but cap the list length
        user_library.user_topics = requested[:5]

    db.add(user_library)
    db.commit()
    db.refresh(user_library)
    return {"message": "Library entry updated", "id": user_library.id}


@router.get("/library/stats")
def get_library_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entries = (
        db.query(UserLibrary)
        .options(joinedload(UserLibrary.article))
        .filter(UserLibrary.user_id == current_user.id)
        .all()
    )

    total_articles = len(entries)
    status_counts = {"unread": 0, "reading": 0, "read": 0}
    ratings: List[int] = []
    topic_counts = defaultdict(int)

    for entry in entries:
        status = entry.status or "unread"
        if status not in status_counts:
            status_counts[status] = 0
        status_counts[status] += 1

        if entry.rating is not None:
            ratings.append(entry.rating)

        topics = (
            entry.user_topics
            if getattr(entry, 'user_topics', None)
            else (entry.article.auto_topics or [TopicClassifier.DEFAULT_TOPIC])
        )
        for topic in topics:
            topic_counts[topic] += 1

    average_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0.0
    default_segments = [
        {"topic": topic, "count": topic_counts.get(topic, 0)}
        for topic in TopicClassifier.default_topics()
    ]

    return {
        "total_articles": total_articles,
        "read_articles": status_counts.get("read", 0),
        "unread_articles": status_counts.get("unread", 0),
        "reading_articles": status_counts.get("reading", 0),
        "average_rating": average_rating,
        "status_distribution": status_counts,
        "topic_distribution": dict(topic_counts),
        "default_segments": default_segments,
    }


@router.get("/library/indexes", response_model=List[UserIndexResponse])
def list_user_indexes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    indexes = (
        db.query(UserIndex)
        .filter(UserIndex.user_id == current_user.id)
        .order_by(UserIndex.created_at.desc())
        .all()
    )
    return indexes


@router.post("/library/indexes", response_model=UserIndexResponse)
def create_user_index(
    payload: UserIndexCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    keywords = [kw.strip() for kw in payload.keywords if kw.strip()]
    if not keywords:
        raise HTTPException(status_code=400, detail="Provide at least one keyword")

    new_index = UserIndex(
        user_id=current_user.id,
        name=payload.name.strip(),
        keywords=keywords,
        color=payload.color or "#2563eb",
    )
    db.add(new_index)
    db.commit()
    db.refresh(new_index)
    return new_index


@router.delete("/library/indexes/{index_id}")
def delete_user_index(
    index_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_index = (
        db.query(UserIndex)
        .filter(UserIndex.id == index_id, UserIndex.user_id == current_user.id)
        .first()
    )
    if not user_index:
        raise HTTPException(status_code=404, detail="Index not found")

    db.delete(user_index)
    db.commit()
    return {"message": "Index deleted"}
