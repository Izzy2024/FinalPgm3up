from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Annotation(Base):
    """
    Model for article annotations and highlights.
    Supports text highlighting with color coding and note-taking.
    """
    __tablename__ = "annotations"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Highlight information
    highlighted_text = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)  # For PDF page reference
    position_data = Column(JSON, nullable=True)  # Store position info (start, end, coordinates)

    # Annotation details
    color = Column(String(20), default="yellow")  # yellow, green, blue, red, purple
    note = Column(Text, nullable=True)  # User's note/comment
    tags = Column(JSON, default=list)  # Tags for categorizing annotations

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    article = relationship("Article", backref="annotations")
    user = relationship("User", backref="annotations")

    def __repr__(self):
        return f"<Annotation(id={self.id}, article_id={self.article_id}, user_id={self.user_id})>"
