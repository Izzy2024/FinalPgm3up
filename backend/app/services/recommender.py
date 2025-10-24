from typing import List, Dict
from difflib import SequenceMatcher
from sqlalchemy.orm import Session
from app.models import Article, UserLibrary


class ArticleRecommender:
    @staticmethod
    def get_recommendations(user_id: int, db: Session, limit: int = 5) -> List[Dict]:
        user_articles = db.query(UserLibrary).filter(
            UserLibrary.user_id == user_id
        ).all()

        if not user_articles:
            return []

        user_keywords = []
        for user_lib in user_articles:
            if user_lib.article.keywords:
                user_keywords.extend(user_lib.article.keywords)

        user_keywords = list(set(user_keywords))

        all_articles = db.query(Article).filter(
            Article.status == "active"
        ).all()

        recommendations = []

        for article in all_articles:
            in_library = any(
                ul.article_id == article.id for ul in user_articles
            )
            if in_library:
                continue

            similarity_score = 0
            if article.keywords:
                common_keywords = set(article.keywords) & set(user_keywords)
                similarity_score = len(common_keywords) / (
                    len(article.keywords) + len(user_keywords)
                ) if (len(article.keywords) + len(user_keywords)) > 0 else 0

            if similarity_score > 0:
                recommendations.append(
                    {
                        "article_id": article.id,
                        "title": article.title,
                        "score": similarity_score,
                        "reason": f"Similar keywords: {', '.join(list(set(article.keywords) & set(user_keywords))[:3])}",
                    }
                )

        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:limit]
