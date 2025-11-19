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

    @staticmethod
    def _calculate_research_score(article: Article) -> float:
        """
        Calculates a 'Research Quality Score' (0.0 to 1.0) for an article
        based on metadata completeness, recency, and academic structure.
        """
        score = 0.0
        
        # 1. Metadata Quality (Max 0.5)
        if article.doi:
            score += 0.2
        if article.journal:
            score += 0.1
        if article.authors and len(article.authors) > 0:
            score += 0.1
        if article.abstract and len(article.abstract) > 50:
            score += 0.1

        # 2. Recency (Max 0.2)
        # Prefer papers from the last 5-10 years
        if article.publication_year:
            current_year = 2025  # Could use datetime.now().year
            age = max(0, current_year - article.publication_year)
            if age <= 5:
                score += 0.2
            elif age <= 10:
                score += 0.1
            elif age <= 20:
                score += 0.05

        # 3. Content/Structure Indicators (Max 0.3)
        # Check for keywords in abstract or auto_topics that suggest research depth
        research_keywords = {
            "methodology", "analysis", "results", "conclusion", 
            "study", "experiment", "data", "survey", "review"
        }
        
        found_keywords = 0
        text_to_check = (article.abstract or "").lower() + " " + " ".join(article.auto_topics or [])
        
        for kw in research_keywords:
            if kw in text_to_check:
                found_keywords += 1
        
        # Cap at 0.3 (e.g., finding 3 keywords gives full points)
        score += min(0.3, found_keywords * 0.1)

        return min(score, 1.0)

    @staticmethod
    def get_library_best_picks(user_id: int, db: Session, limit: int = 10) -> List[Dict]:
        """
        Analyzes the user's OWN library and returns the highest quality research papers.
        """
        user_articles_list = db.query(UserLibrary).filter(
            UserLibrary.user_id == user_id
        ).all()

        if not user_articles_list:
            return []

        scored_articles = []
        for ul in user_articles_list:
            article = ul.article
            quality_score = ArticleRecommender._calculate_research_score(article)
            
            # Generate reason based on score components
            reasons = []
            if article.doi:
                reasons.append("Verified DOI")
            if article.publication_year and article.publication_year >= 2020:
                reasons.append("Recent Publication")
            if quality_score > 0.7:
                reasons.append("High Academic Impact")
            
            scored_articles.append({
                "article_id": article.id,
                "title": article.title,
                "authors": article.authors or [],
                "score": round(quality_score, 2),
                "reason": " | ".join(reasons) if reasons else "Good Reference",
                "journal": article.journal,
                "year": article.publication_year
            })

        # Sort by score descending
        scored_articles.sort(key=lambda x: x["score"], reverse=True)
        
        return scored_articles[:limit]
