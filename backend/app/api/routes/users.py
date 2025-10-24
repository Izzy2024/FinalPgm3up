from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.schemas import UserResponse, UserUpdate
from app.models import User, Article, UserLibrary

router = APIRouter(prefix="/api/users", tags=["users"])


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


@router.get("/library/")
def get_user_library(
    skip: int = 0,
    limit: int = 10,
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(UserLibrary).filter(UserLibrary.user_id == current_user.id)
    
    if status:
        query = query.filter(UserLibrary.status == status)
    
    user_libraries = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "total": total,
        "items": [
            {
                "id": ul.id,
                "article_id": ul.article_id,
                "title": ul.article.title,
                "authors": ul.article.authors,
                "status": ul.status,
                "rating": ul.rating,
                "notes": ul.notes,
                "added_at": ul.added_at,
                "updated_at": ul.updated_at,
            }
            for ul in user_libraries
        ]
    }


@router.put("/library/{article_id}")
def update_library_entry(
    article_id: int,
    status: str = None,
    rating: int = None,
    notes: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_library = db.query(UserLibrary).filter(
        UserLibrary.user_id == current_user.id,
        UserLibrary.article_id == article_id
    ).first()
    if not user_library:
        raise HTTPException(status_code=404, detail="Article not in library")

    if status:
        user_library.status = status
    if rating is not None:
        if rating < 0 or rating > 5:
            raise HTTPException(status_code=400, detail="Rating must be between 0 and 5")
        user_library.rating = rating
    if notes is not None:
        user_library.notes = notes

    db.add(user_library)
    db.commit()
    db.refresh(user_library)
    return {"message": "Library entry updated", "id": user_library.id}


@router.get("/library/stats")
def get_library_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    total_articles = db.query(UserLibrary).filter(
        UserLibrary.user_id == current_user.id
    ).count()
    
    read_articles = db.query(UserLibrary).filter(
        UserLibrary.user_id == current_user.id,
        UserLibrary.status == "read"
    ).count()
    
    avg_rating = db.query(func.avg(UserLibrary.rating)).filter(
        UserLibrary.user_id == current_user.id,
        UserLibrary.rating.isnot(None)
    ).scalar() or 0

    status_counts = {}
    for status in ["unread", "reading", "read"]:
        count = db.query(UserLibrary).filter(
            UserLibrary.user_id == current_user.id,
            UserLibrary.status == status
        ).count()
        status_counts[status] = count

    return {
        "total_articles": total_articles,
        "read_articles": read_articles,
        "unread_articles": total_articles - read_articles,
        "average_rating": round(float(avg_rating), 2),
        "status_distribution": status_counts
    }
