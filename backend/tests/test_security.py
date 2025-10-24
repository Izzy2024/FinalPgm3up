import pytest
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from datetime import timedelta


def test_password_hashing():
    """Test password hashing and verification"""
    password = "mySecurePassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongPassword", hashed) is False


def test_access_token_creation():
    """Test JWT access token creation"""
    data = {"sub": "testuser"}
    token = create_access_token(data=data)
    
    assert isinstance(token, str)
    assert len(token) > 0
    assert "." in token  # JWT has 3 parts separated by dots


def test_access_token_expiry():
    """Test access token with custom expiry"""
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=5)
    token = create_access_token(data=data, expires_delta=expires_delta)
    
    assert isinstance(token, str)
    assert len(token) > 0


def test_password_different_hashes():
    """Test that same password produces different hashes (due to salt)"""
    password = "samePassword"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    assert hash1 != hash2
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True
