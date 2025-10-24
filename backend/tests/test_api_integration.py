import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import User, Article, UserLibrary
from app.core.security import get_password_hash

client = TestClient(app)


@pytest.fixture
def test_user(test_client, db):
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("password123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user, test_client):
    response = test_client.post(
        "/api/auth/token",
        data={"username": "testuser", "password": "password123"}
    )
    return response.json()["access_token"]


class TestArticlesAPI:
    def test_list_articles_no_auth(self, test_client):
        response = test_client.get("/api/articles/")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_articles_with_filter(self, test_client, db):
        article = Article(
            title="Test Article",
            authors=["Author"],
            status="active",
            file_path="test.pdf",
            file_hash="hash123"
        )
        db.add(article)
        db.commit()

        response = test_client.get("/api/articles/")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["title"] == "Test Article"

    def test_get_article(self, test_client, db):
        article = Article(
            title="Test Article",
            authors=["Author"],
            status="active",
            file_path="test.pdf",
            file_hash="hash123"
        )
        db.add(article)
        db.commit()
        db.refresh(article)

        response = test_client.get(f"/api/articles/{article.id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Test Article"

    def test_get_nonexistent_article(self, test_client):
        response = test_client.get("/api/articles/99999")
        assert response.status_code == 404

    def test_delete_article_unauthorized(self, test_client, db):
        user = User(
            username="otheruser",
            email="other@example.com",
            password_hash=get_password_hash("password123")
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        article = Article(
            title="Test Article",
            authors=["Author"],
            status="active",
            file_path="test.pdf",
            file_hash="hash123",
            uploaded_by=user.id
        )
        db.add(article)
        db.commit()
        db.refresh(article)

        response = test_client.delete(
            f"/api/articles/{article.id}",
            headers={"Authorization": "Bearer invalid"}
        )
        assert response.status_code == 401


class TestRecommendationsAPI:
    def test_get_recommendations_no_auth(self, test_client):
        response = test_client.get("/api/recommendations/")
        assert response.status_code == 401

    def test_get_recommendations_no_articles(self, test_client, test_user, auth_token):
        response = test_client.get(
            "/api/recommendations/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert response.json()["recommendations"] == []

    def test_get_recommendations_with_articles(self, test_client, test_user, auth_token, db):
        article1 = Article(
            title="ML Article 1",
            authors=["Author1"],
            keywords=["machine learning"],
            status="active",
            file_path="test1.pdf",
            file_hash="hash1"
        )
        article2 = Article(
            title="ML Article 2",
            authors=["Author2"],
            keywords=["machine learning", "AI"],
            status="active",
            file_path="test2.pdf",
            file_hash="hash2"
        )
        db.add_all([article1, article2])
        db.commit()
        db.refresh(article1)
        db.refresh(article2)

        user_lib = UserLibrary(user_id=test_user.id, article_id=article1.id)
        db.add(user_lib)
        db.commit()

        response = test_client.get(
            "/api/recommendations/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        recs = response.json()["recommendations"]
        assert len(recs) > 0
