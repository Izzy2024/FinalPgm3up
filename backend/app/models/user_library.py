from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class UserLibrary(Base):
    __tablename__ = "user_libraries"
    __table_args__ = (UniqueConstraint("user_id", "article_id", name="uq_user_article"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    status = Column(String(20), default="unread")
    notes = Column(Text)
    rating = Column(Integer)
    added_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="user_libraries")
    article = relationship("Article", back_populates="user_libraries")

    def __repr__(self):
        return f"<UserLibrary(user_id={self.user_id}, article_id={self.article_id})>"
