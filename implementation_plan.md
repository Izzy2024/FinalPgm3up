# Implementation Plan - Research Quality Recommendations

## Goal
Implement a recommendation system that analyzes the user's *existing* library to highlight "high-grade" research documents. This transforms the "Recommendations" feature to include a "Quality Analysis" of the user's own collection.

## User Review Required
> [!IMPORTANT]
> I am interpreting "recommend documents that I have in my library" as a request to **analyze and rank existing files** based on research quality (metadata completeness, academic structure, recency), rather than finding new external papers.

## Proposed Changes

### Backend

#### [MODIFY] [recommender.py](file:///Users/admin/Documents/UP/proyectofinal/backend/app/services/recommender.py)
- Add `calculate_research_score(article)` method.
  - **Scoring Criteria:**
    - **Metadata Quality (40%)**: Presence of DOI, Abstract, Authors, Journal.
    - **Recency (20%)**: Newer papers get higher scores.
    - **Content Depth (20%)**: Based on file size/page count (proxy) or keyword count.
    - **Academic Structure (20%)**: Checks for "Introduction", "Methodology", "Results" keywords in abstract/content if available.
- Add `get_library_best_picks(user_id, db, limit)` method.

#### [MODIFY] [recommendations.py](file:///Users/admin/Documents/UP/proyectofinal/backend/app/api/routes/recommendations.py)
- Add `scope` query parameter to `get_recommendations`.
  - `scope="discover"` (default): Current behavior (find new papers).
  - `scope="library"`: New behavior (analyze my papers).

### Frontend

#### [MODIFY] [Recommendations.tsx](file:///Users/admin/Documents/UP/proyectofinal/frontend/src/pages/Recommendations.tsx)
- Add a **Toggle/Tab System**: "Discover New" vs "My Top Research".
- Update the UI to display the "Research Score" prominently for library items.
- Remove "Add to Library" button for items already in the library (obviously).
- Add "Read Now" button for library items.

## Verification Plan

### Automated Tests
- Run backend tests to ensure scoring logic doesn't crash.
- `pytest tests/test_recommender.py` (if exists, or create simple test).

### Manual Verification
1.  Upload a few PDFs (some "good" with metadata, some "bad").
2.  Go to Recommendations page.
3.  Switch to "My Top Research".
4.  Verify the "good" papers are ranked higher.
