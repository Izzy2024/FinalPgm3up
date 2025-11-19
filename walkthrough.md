# Walkthrough - Research Quality Analysis Implementation

## Changes

### Backend
- **`app/services/recommender.py`**: Added `_calculate_research_score` method to evaluate articles based on:
    - Metadata (DOI, Authors, Journal)
    - Recency (Publication Year)
    - Content Structure (Keywords like "Methodology", "Results")
- **`app/services/recommender.py`**: Added `get_library_best_picks` to apply this scoring to the user's own library.
- **`app/api/routes/recommendations.py`**: Updated endpoint to accept `scope="library"` parameter.
- **`app/api/routes/articles.py`**: Added `get_article_file` endpoint to serve PDF files.

### Frontend
- **`src/services/api.ts`**: Updated `recommendationsAPI.get` to accept `scope`.
- **`src/pages/Recommendations.tsx`**: Completely redesigned to:
    - Fetch with `scope="library"`.
    - Display "Research Quality Analysis" header.
    - Show "Research Score" badges (High Impact, Good Reference).
    - Provide "Read Now" button instead of "Add to Library".
- **`src/pages/ArticleReader.tsx`**: Created new component to view PDFs within the app.
- **`src/App.tsx`**: Added route `/library/article/:id` pointing to `ArticleReader`.

## Verification Results

### Automated Tests
- [ ] Run backend tests: `pytest` (Pending user run)
- [ ] Run frontend tests: `npm test` (Pending user run)

### Manual Verification Steps
1.  **Login** to the application.
2.  **Upload** a few PDF articles (ensure some have metadata/DOIs and others don't).
3.  Navigate to the **"Recommendations"** page (now "Research Quality Analysis").
4.  **Verify** that:
    - The page title is "Research Quality Analysis".
    - Articles from your library are listed.
    - Articles with better metadata/recency have higher scores and "High Impact" badges.
    - Clicking "Read Now" takes you to the article reader.
    - **Verify** that the PDF loads correctly in the viewer.
