from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.schemas import AnnotationResponse, AnnotationCreate, AnnotationUpdate
from app.models import User, Article, Annotation
import logging

router = APIRouter(prefix="/api/annotations", tags=["annotations"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=AnnotationResponse)
def create_annotation(
    annotation: AnnotationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new annotation/highlight for an article.
    """
    # Verify article exists
    article = db.query(Article).filter(Article.id == annotation.article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Validate color
    valid_colors = ["yellow", "green", "blue", "red", "purple"]
    if annotation.color and annotation.color not in valid_colors:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid color. Must be one of: {', '.join(valid_colors)}"
        )

    new_annotation = Annotation(
        article_id=annotation.article_id,
        user_id=current_user.id,
        highlighted_text=annotation.highlighted_text,
        page_number=annotation.page_number,
        position_data=annotation.position_data,
        color=annotation.color,
        note=annotation.note,
        tags=annotation.tags or [],
    )

    db.add(new_annotation)
    db.commit()
    db.refresh(new_annotation)

    logger.info(f"Annotation created: {new_annotation.id} for article {annotation.article_id}")
    return new_annotation


@router.get("/article/{article_id}", response_model=List[AnnotationResponse])
def get_article_annotations(
    article_id: int,
    color: Optional[str] = None,
    tag: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all annotations for a specific article by the current user.
    Optional filters: color, tag
    """
    # Verify article exists
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    query = db.query(Annotation).filter(
        Annotation.article_id == article_id,
        Annotation.user_id == current_user.id
    )

    # Filter by color
    if color:
        query = query.filter(Annotation.color == color)

    # Filter by tag (check if tag exists in tags array)
    if tag:
        query = query.filter(Annotation.tags.contains([tag]))

    annotations = query.order_by(Annotation.created_at.desc()).all()
    return annotations


@router.get("/my-annotations", response_model=List[AnnotationResponse])
def get_my_annotations(
    skip: int = 0,
    limit: int = 50,
    article_id: Optional[int] = None,
    color: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all annotations by the current user across all articles.
    """
    query = db.query(Annotation).filter(Annotation.user_id == current_user.id)

    if article_id:
        query = query.filter(Annotation.article_id == article_id)

    if color:
        query = query.filter(Annotation.color == color)

    annotations = query.order_by(Annotation.created_at.desc()).offset(skip).limit(limit).all()
    return annotations


@router.get("/{annotation_id}", response_model=AnnotationResponse)
def get_annotation(
    annotation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific annotation by ID.
    """
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")

    # Verify ownership
    if annotation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this annotation")

    return annotation


@router.put("/{annotation_id}", response_model=AnnotationResponse)
def update_annotation(
    annotation_id: int,
    annotation_update: AnnotationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an annotation.
    """
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")

    # Verify ownership
    if annotation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this annotation")

    # Validate color if provided
    if annotation_update.color:
        valid_colors = ["yellow", "green", "blue", "red", "purple"]
        if annotation_update.color not in valid_colors:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid color. Must be one of: {', '.join(valid_colors)}"
            )

    # Update fields
    update_data = annotation_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(annotation, field, value)

    db.add(annotation)
    db.commit()
    db.refresh(annotation)

    logger.info(f"Annotation updated: {annotation_id}")
    return annotation


@router.delete("/{annotation_id}")
def delete_annotation(
    annotation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete an annotation.
    """
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")

    # Verify ownership
    if annotation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this annotation")

    db.delete(annotation)
    db.commit()

    logger.info(f"Annotation deleted: {annotation_id}")
    return {"message": "Annotation deleted successfully"}


@router.get("/article/{article_id}/stats")
def get_article_annotation_stats(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get statistics about annotations for an article.
    Returns count by color, total annotations, etc.
    """
    # Verify article exists
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    annotations = db.query(Annotation).filter(
        Annotation.article_id == article_id,
        Annotation.user_id == current_user.id
    ).all()

    # Count by color
    color_counts = {}
    for annotation in annotations:
        color = annotation.color or "yellow"
        color_counts[color] = color_counts.get(color, 0) + 1

    # Collect all unique tags
    all_tags = set()
    for annotation in annotations:
        if annotation.tags:
            all_tags.update(annotation.tags)

    return {
        "article_id": article_id,
        "total_annotations": len(annotations),
        "color_distribution": color_counts,
        "tags": list(all_tags),
        "annotations_with_notes": sum(1 for a in annotations if a.note),
    }
