from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, BigInteger, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    authors = Column(JSON, default=[])
    abstract = Column(Text)
    keywords = Column(JSON, default=[])
    publication_year = Column(Integer)
    journal = Column(String(200))
    doi = Column(String(100), unique=True, nullable=True, index=True)
    file_path = Column(String(500))
    file_size = Column(BigInteger)
    file_hash = Column(String(64), unique=True, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="articles")
    uploaded_by_user = relationship("User", back_populates="articles")
    user_libraries = relationship("UserLibrary", back_populates="article")
    recommendations = relationship("Recommendation", back_populates="article")

    def __repr__(self):
        return f"<Article(title={self.title}, doi={self.doi})>"
