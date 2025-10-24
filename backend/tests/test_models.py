import pytest
from app.models.user import User
from app.core.security import hash_password
from datetime import datetime


def test_user_creation(db):
    """Test creating a new user"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("password123"),
        first_name="Test",
        last_name="User",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True


def test_user_unique_email(db):
    """Test email uniqueness constraint"""
    user1 = User(
        username="user1",
        email="same@example.com",
        password_hash=hash_password("pass1"),
    )
    user2 = User(
        username="user2",
        email="same@example.com",
        password_hash=hash_password("pass2"),
    )
    
    db.add(user1)
    db.commit()
    db.add(user2)
    
    with pytest.raises(Exception):
        db.commit()


def test_user_unique_username(db):
    """Test username uniqueness constraint"""
    user1 = User(
        username="duplicate",
        email="email1@example.com",
        password_hash=hash_password("pass1"),
    )
    user2 = User(
        username="duplicate",
        email="email2@example.com",
        password_hash=hash_password("pass2"),
    )
    
    db.add(user1)
    db.commit()
    db.add(user2)
    
    with pytest.raises(Exception):
        db.commit()


def test_user_timestamps(db):
    """Test user creation and update timestamps"""
    user = User(
        username="timetest",
        email="time@example.com",
        password_hash=hash_password("pass"),
    )
    db.add(user)
    db.commit()
    
    assert user.created_at is not None
    assert user.updated_at is not None
    assert isinstance(user.created_at, datetime)
