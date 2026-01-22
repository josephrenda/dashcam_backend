"""
User database model.
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean
from app.core.database import Base


class User(Base):
    """User model for authentication and profile management."""
    __tablename__ = "users"
    
    user_id = Column(String(36), primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)