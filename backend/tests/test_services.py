import pytest
import os
import tempfile
from pathlib import Path
from app.services.metadata_extractor import MetadataExtractor
from app.services.classifier import ArticleClassifier
from app.services.recommender import ArticleRecommender
from app.services.bibliography_generator import BibliographyGenerator
from app.models import Article, User, UserLibrary, Category
from sqlalchemy.orm import Session


class TestMetadataExtractor:
    def test_calculate_file_hash(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test content")
            tmp.flush()
            hash1 = MetadataExtractor.calculate_file_hash(tmp.name)
            hash2 = MetadataExtractor.calculate_file_hash(tmp.name)
            assert hash1 == hash2
            assert len(hash1) == 64
            os.unlink(tmp.name)

    def test_calculate_different_hashes(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp1:
            tmp1.write(b"content1")
            tmp1.flush()
            hash1 = MetadataExtractor.calculate_file_hash(tmp1.name)

        with tempfile.NamedTemporaryFile(delete=False) as tmp2:
            tmp2.write(b"content2")
            tmp2.flush()
            hash2 = MetadataExtractor.calculate_file_hash(tmp2.name)

        assert hash1 != hash2
        os.unlink(tmp1.name)
        os.unlink(tmp2.name)

    def test_extract_from_pdf_nonexistent(self):
        result = MetadataExtractor.extract_from_pdf("/nonexistent/file.pdf")
        assert result["title"] is None
        assert result["authors"] == []
        assert result["abstract"] is None


class TestArticleClassifier:
    def test_classifier_initialization(self):
        classifier = ArticleClassifier()
        assert not classifier.is_trained
        assert classifier.categories == {}

    def test_classifier_predict_untrained(self):
        classifier = ArticleClassifier()
        result = classifier.predict("test text")
        assert result == 0

    def test_classifier_training(self):
        classifier = ArticleClassifier()
        texts = [
            "machine learning algorithms",
            "neural networks and AI",
            "deep learning frameworks",
            "statistical analysis",
            "data patterns",
        ]
        labels = [0, 0, 0, 1, 1]
        classifier.train(texts, labels)
        assert classifier.is_trained

    def test_classify_by_keywords(self):
        classifier = ArticleClassifier()
        scores = classifier.classify_by_keywords(
            title="Deep Learning in Medicine",
            abstract="Using neural networks for medical diagnosis",
            keywords=["machine learning", "medical", "deep learning"],
        )
        assert isinstance(scores, dict)
        assert "Artificial Intelligence" in scores
        assert "Medicine" in scores
        assert scores["Artificial Intelligence"] > 0
        assert scores["Medicine"] > 0

    def test_classify_by_keywords_empty(self):
        classifier = ArticleClassifier()
        scores = classifier.classify_by_keywords(
            title="", abstract="", keywords=[]
        )
        assert all(score == 0 for score in scores.values())


class TestArticleRecommender:
    def test_get_recommendations_no_articles(self, db: Session):
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashedpwd"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        recommendations = ArticleRecommender.get_recommendations(user.id, db)
        assert recommendations == []

    def test_get_recommendations_with_articles(self, db: Session):
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashedpwd"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        article1 = Article(
            title="ML Article",
            authors=["Author1"],
            keywords=["machine learning", "AI"],
            status="active",
            file_path="test.pdf",
            file_hash="hash1"
        )
        article2 = Article(
            title="ML Article 2",
            authors=["Author2"],
            keywords=["machine learning", "neural networks"],
            status="active",
            file_path="test2.pdf",
            file_hash="hash2"
        )
        article3 = Article(
            title="Biology Article",
            authors=["Author3"],
            keywords=["cell", "biology"],
            status="active",
            file_path="test3.pdf",
            file_hash="hash3"
        )
        db.add_all([article1, article2, article3])
        db.commit()
        db.refresh(article1)
        db.refresh(article2)
        db.refresh(article3)

        user_lib = UserLibrary(user_id=user.id, article_id=article1.id)
        db.add(user_lib)
        db.commit()

        recommendations = ArticleRecommender.get_recommendations(user.id, db, limit=5)
        assert len(recommendations) > 0
        assert any(rec["article_id"] == article2.id for rec in recommendations)
        assert not any(rec["article_id"] == article1.id for rec in recommendations)

    def test_get_recommendations_limit(self, db: Session):
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashedpwd"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        article1 = Article(
            title="Article 1",
            authors=["Author"],
            keywords=["test"],
            status="active",
            file_path="test.pdf",
            file_hash="hash1"
        )
        db.add(article1)
        db.commit()
        db.refresh(article1)

        user_lib = UserLibrary(user_id=user.id, article_id=article1.id)
        db.add(user_lib)
        db.commit()

        for i in range(10):
            article = Article(
                title=f"Article {i+2}",
                authors=["Author"],
                keywords=["test"],
                status="active",
                file_path=f"test{i}.pdf",
                file_hash=f"hash{i+2}"
            )
            db.add(article)
        db.commit()

        recommendations = ArticleRecommender.get_recommendations(user.id, db, limit=3)
        assert len(recommendations) <= 3


class TestBibliographyGenerator:
    def _create_test_article(self, db: Session) -> Article:
        article = Article(
            title="Test Article",
            authors=["John Doe", "Jane Smith"],
            journal="Science Review",
            publication_year=2023,
            doi="10.1234/test",
            file_path="test.pdf",
            file_hash="testhash"
        )
        db.add(article)
        db.commit()
        db.refresh(article)
        return article

    def test_generate_apa(self, db: Session):
        article = self._create_test_article(db)
        bib = BibliographyGenerator.generate_apa(article)
        assert "John Doe" in bib
        assert "Jane Smith" in bib
        assert "2023" in bib
        assert "Test Article" in bib
        assert "Science Review" in bib
        assert "10.1234/test" in bib

    def test_generate_mla(self, db: Session):
        article = self._create_test_article(db)
        bib = BibliographyGenerator.generate_mla(article)
        assert "John Doe" in bib
        assert "2023" in bib
        assert "Test Article" in bib

    def test_generate_chicago(self, db: Session):
        article = self._create_test_article(db)
        bib = BibliographyGenerator.generate_chicago(article)
        assert "John Doe" in bib
        assert "2023" in bib
        assert "Test Article" in bib

    def test_generate_bibtex(self, db: Session):
        article = self._create_test_article(db)
        bib = BibliographyGenerator.generate_bibtex(article)
        assert "@article" in bib
        assert "John Doe" in bib
        assert "2023" in bib
        assert "doi = {10.1234/test}" in bib

    def test_generate_ris(self, db: Session):
        article = self._create_test_article(db)
        bib = BibliographyGenerator.generate_ris(article)
        assert "TY  - JOUR" in bib
        assert "AU  - John Doe" in bib
        assert "AU  - Jane Smith" in bib
        assert "PY  - 2023" in bib
        assert "ER  -" in bib

    def test_generate_with_missing_fields(self, db: Session):
        article = Article(
            title="Minimal Article",
            authors=[],
            file_path="test.pdf",
            file_hash="testhash"
        )
        db.add(article)
        db.commit()
        db.refresh(article)

        apa = BibliographyGenerator.generate_apa(article)
        assert "Unknown" in apa
        mla = BibliographyGenerator.generate_mla(article)
        assert "Unknown" in mla
