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


@pytest.fixture
def test_articles(db):
    articles = [
        Article(
            title="ML Article 1",
            authors=["Author1"],
            keywords=["machine learning"],
            status="active",
            file_path="test1.pdf",
            file_hash="hash1"
        ),
        Article(
            title="ML Article 2",
            authors=["Author2"],
            keywords=["machine learning", "AI"],
            status="active",
            file_path="test2.pdf",
            file_hash="hash2"
        ),
        Article(
            title="Biology Article",
            authors=["Author3"],
            keywords=["cell", "biology"],
            status="active",
            file_path="test3.pdf",
            file_hash="hash3"
        ),
    ]
    db.add_all(articles)
    db.commit()
    for article in articles:
        db.refresh(article)
    return articles


class TestUserLibraryAPI:
    def test_add_to_library(self, test_client, test_user, auth_token, test_articles, db):
        article = test_articles[0]
        response = test_client.post(
            f"/api/users/library/{article.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert "added to library" in response.json()["message"]

        user_lib = db.query(UserLibrary).filter(
            UserLibrary.user_id == test_user.id,
            UserLibrary.article_id == article.id
        ).first()
        assert user_lib is not None
        assert user_lib.status == "unread"

    def test_add_duplicate_to_library(self, test_client, test_user, auth_token, test_articles, db):
        article = test_articles[0]
        test_client.post(
            f"/api/users/library/{article.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        response = test_client.post(
            f"/api/users/library/{article.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 400
        assert "already in library" in response.json()["detail"]

    def test_remove_from_library(self, test_client, test_user, auth_token, test_articles, db):
        article = test_articles[0]
        user_lib = UserLibrary(user_id=test_user.id, article_id=article.id)
        db.add(user_lib)
        db.commit()

        response = test_client.delete(
            f"/api/users/library/{article.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert "removed from library" in response.json()["message"]

        user_lib = db.query(UserLibrary).filter(
            UserLibrary.user_id == test_user.id,
            UserLibrary.article_id == article.id
        ).first()
        assert user_lib is None

    def test_get_user_library_empty(self, test_client, test_user, auth_token):
        response = test_client.get(
            "/api/users/library/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_get_user_library_with_articles(self, test_client, test_user, auth_token, test_articles, db):
        for article in test_articles[:2]:
            user_lib = UserLibrary(user_id=test_user.id, article_id=article.id)
            db.add(user_lib)
        db.commit()

        response = test_client.get(
            "/api/users/library/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
        assert data["items"][0]["title"] == "ML Article 1"

    def test_get_user_library_filter_by_status(self, test_client, test_user, auth_token, test_articles, db):
        article1 = test_articles[0]
        article2 = test_articles[1]
        
        ul1 = UserLibrary(user_id=test_user.id, article_id=article1.id, status="read")
        ul2 = UserLibrary(user_id=test_user.id, article_id=article2.id, status="unread")
        db.add_all([ul1, ul2])
        db.commit()

        response = test_client.get(
            "/api/users/library/?status=read",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "read"

    def test_update_library_entry(self, test_client, test_user, auth_token, test_articles, db):
        article = test_articles[0]
        user_lib = UserLibrary(user_id=test_user.id, article_id=article.id)
        db.add(user_lib)
        db.commit()

        response = test_client.put(
            f"/api/users/library/{article.id}?status=read&rating=4&notes=Good paper",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200

        user_lib = db.query(UserLibrary).filter(
            UserLibrary.user_id == test_user.id,
            UserLibrary.article_id == article.id
        ).first()
        assert user_lib.status == "read"
        assert user_lib.rating == 4
        assert user_lib.notes == "Good paper"

    def test_update_library_entry_invalid_rating(self, test_client, test_user, auth_token, test_articles, db):
        article = test_articles[0]
        user_lib = UserLibrary(user_id=test_user.id, article_id=article.id)
        db.add(user_lib)
        db.commit()

        response = test_client.put(
            f"/api/users/library/{article.id}?rating=10",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 400
        assert "Rating must be between 0 and 5" in response.json()["detail"]

    def test_get_library_stats(self, test_client, test_user, auth_token, test_articles, db):
        article1 = test_articles[0]
        article2 = test_articles[1]
        article3 = test_articles[2]
        
        ul1 = UserLibrary(user_id=test_user.id, article_id=article1.id, status="read", rating=5)
        ul2 = UserLibrary(user_id=test_user.id, article_id=article2.id, status="reading", rating=4)
        ul3 = UserLibrary(user_id=test_user.id, article_id=article3.id, status="unread")
        db.add_all([ul1, ul2, ul3])
        db.commit()

        response = test_client.get(
            "/api/users/library/stats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        stats = response.json()
        assert stats["total_articles"] == 3
        assert stats["read_articles"] == 1
        assert stats["unread_articles"] == 2
        assert stats["average_rating"] == 4.5
        assert stats["status_distribution"]["read"] == 1
        assert stats["status_distribution"]["reading"] == 1
        assert stats["status_distribution"]["unread"] == 1

    def test_get_library_stats_empty(self, test_client, test_user, auth_token):
        response = test_client.get(
            "/api/users/library/stats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        stats = response.json()
        assert stats["total_articles"] == 0
        assert stats["average_rating"] == 0
