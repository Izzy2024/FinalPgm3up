from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.recommender import ArticleRecommender
from app.models import User

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("/")
def get_recommendations(
    limit: int = 5,
    scope: str = "discover",  # "discover" or "library"
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if scope == "library":
        recommendations = ArticleRecommender.get_library_best_picks(
            current_user.id, db, limit
        )
    else:
        recommendations = ArticleRecommender.get_recommendations(
            current_user.id, db, limit
        )
    
    return {"recommendations": recommendations}
