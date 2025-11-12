from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    institution = Column(String(100))
    field_of_study = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    articles = relationship("Article", back_populates="uploaded_by_user")
    user_libraries = relationship("UserLibrary", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")
    categories = relationship("Category", back_populates="created_by_user")
    indexes = relationship("UserIndex", back_populates="user")

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"
