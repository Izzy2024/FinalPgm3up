from typing import List, Dict
from difflib import SequenceMatcher
from sqlalchemy.orm import Session
from app.models import Article, UserLibrary


class ArticleRecommender:
    @staticmethod
    def _calculate_similarity_score(user_article: Article, candidate_article: Article) -> float:
        score = 0.0
        
        if user_article.keywords and candidate_article.keywords:
            common_keywords = set(user_article.keywords) & set(candidate_article.keywords)
            keyword_similarity = len(common_keywords) / max(
                len(user_article.keywords), len(candidate_article.keywords), 1
            )
            score += keyword_similarity * 0.5

        if user_article.journal and candidate_article.journal:
            if user_article.journal.lower() == candidate_article.journal.lower():
                score += 0.3

        if user_article.publication_year and candidate_article.publication_year:
            year_diff = abs(user_article.publication_year - candidate_article.publication_year)
            year_similarity = max(0, 1 - (year_diff / 10))
            score += year_similarity * 0.2

        return min(score, 1.0)

    @staticmethod
    def get_recommendations(user_id: int, db: Session, limit: int = 5) -> List[Dict]:
        user_articles_list = db.query(UserLibrary).filter(
            UserLibrary.user_id == user_id
        ).all()

        if not user_articles_list:
            return []

        user_articles = [ul.article for ul in user_articles_list]
        user_article_ids = set(ul.article_id for ul in user_articles_list)

        user_keywords = []
        for article in user_articles:
            if article.keywords:
                user_keywords.extend(article.keywords)
        user_keywords = list(set(user_keywords))

        all_articles = db.query(Article).filter(
            Article.status == "active"
        ).all()

        recommendations = []

        for candidate in all_articles:
            if candidate.id in user_article_ids:
                continue

            similarity_score = 0.0
            reason_parts = []

            for user_article in user_articles:
                candidate_score = ArticleRecommender._calculate_similarity_score(
                    user_article, candidate
                )
                similarity_score = max(similarity_score, candidate_score)

            if candidate.keywords and user_keywords:
                common_keywords = set(candidate.keywords) & set(user_keywords)
                if common_keywords:
                    reason_parts.append(
                        f"Similar keywords: {', '.join(list(common_keywords)[:3])}"
                    )

            if candidate.journal and any(
                a.journal and a.journal.lower() == candidate.journal.lower() 
                for a in user_articles
            ):
                reason_parts.append("Same journal")

            if similarity_score > 0:
                recommendations.append(
                    {
                        "article_id": candidate.id,
                        "title": candidate.title,
                        "authors": candidate.authors or [],
                        "score": round(similarity_score, 3),
                        "reason": " | ".join(reason_parts) if reason_parts else "Related content",
                    }
                )

        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:limit]
