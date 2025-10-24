from sqlalchemy import Column, Integer, DateTime, ForeignKey, DECIMAL, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    score = Column(DECIMAL(3, 2))
    reason = Column(String(200))
    is_viewed = Column(String(20), default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="recommendations")
    article = relationship("Article", back_populates="recommendations")

    def __repr__(self):
        return f"<Recommendation(user_id={self.user_id}, article_id={self.article_id})>"
