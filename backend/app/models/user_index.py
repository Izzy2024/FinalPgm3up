from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class UserIndex(Base):
    __tablename__ = "user_indexes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    keywords = Column(ARRAY(String), default=list)
    color = Column(String(20), default="#2563eb")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="indexes")

    def __repr__(self):
        return f"<UserIndex(name={self.name}, user_id={self.user_id})>"
