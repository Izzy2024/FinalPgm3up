import pytest
from app.core.security import get_password_hash
from app.models.user import User


def test_register_endpoint(test_client, db):
    """Test user registration"""
    response = test_client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "first_name": "New",
            "last_name": "User",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data


def test_register_duplicate_email(test_client, db):
    """Test registration with duplicate email"""
    user = User(
        username="existing",
        email="existing@example.com",
        password_hash=get_password_hash("pass"),
    )
    db.add(user)
    db.commit()
    
    response = test_client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "email": "existing@example.com",
            "password": "password123",
        },
    )
    
    assert response.status_code == 400


def test_login_endpoint(test_client, db):
    """Test user login"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("password123"),
    )
    db.add(user)
    db.commit()
    
    response = test_client.post(
        "/api/auth/token",
        data={
            "username": "testuser",
            "password": "password123",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(test_client, db):
    """Test login with invalid credentials"""
    response = test_client.post(
        "/api/auth/token",
        data={
            "username": "nonexistent",
            "password": "wrongpassword",
        },
    )
    
    assert response.status_code == 401


def test_get_current_user(test_client, db):
    """Test getting current authenticated user"""
    user = User(
        username="authtest",
        email="auth@example.com",
        password_hash=get_password_hash("password123"),
    )
    db.add(user)
    db.commit()
    
    # First login to get token
    login_response = test_client.post(
        "/api/auth/token",
        data={
            "username": "authtest",
            "password": "password123",
        },
    )
    
    token = login_response.json()["access_token"]
    
    # Use token to get current user
    response = test_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "authtest"
    assert data["email"] == "auth@example.com"
