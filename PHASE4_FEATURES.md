# Phase 4 Features - Advanced Filtering and Annotations

This document describes the new features implemented for Phase 4 of the SIGRAA project.

## Features Implemented

### 1. Advanced Filtering by Date Range and Keywords

Enhanced article search capabilities with multiple filter options.

#### Backend Implementation

**File**: `backend/app/api/routes/articles.py`

The `/api/articles/` endpoint now supports the following query parameters:

- `keyword`: Search in title, abstract, keywords array, and authors array (case-insensitive)
- `start_year`: Filter articles published from this year onwards
- `end_year`: Filter articles published up to this year
- `start_date`: Filter articles uploaded from this date (format: YYYY-MM-DD)
- `end_date`: Filter articles uploaded up to this date (format: YYYY-MM-DD)
- `category_id`: Filter by category (existing feature)
- `skip`, `limit`: Pagination (existing features)

**Example API Calls**:

```bash
# Search for articles with keyword "machine learning"
GET /api/articles/?keyword=machine%20learning

# Get articles published between 2020 and 2023
GET /api/articles/?start_year=2020&end_year=2023

# Get articles uploaded in the last week
GET /api/articles/?start_date=2025-11-02&end_date=2025-11-09

# Combined filters
GET /api/articles/?keyword=neural&start_year=2020&category_id=1
```

#### Frontend Implementation

**Component**: `frontend/src/components/ui/AdvancedFilter.tsx`

A reusable React component that provides a UI for advanced filtering:

**Features**:
- Keyword search across multiple fields
- Publication year range selector
- Upload date range picker
- Category dropdown
- Filter state management
- Clear all filters functionality
- Visual indicator for active filters

**Usage Example**:

```tsx
import { AdvancedFilter, FilterOptions } from './components/ui';

function ArticleList() {
  const [filters, setFilters] = useState<FilterOptions>({});

  const handleFilterChange = (newFilters: FilterOptions) => {
    setFilters(newFilters);
    // Fetch articles with new filters
    articlesAPI.list({
      skip: 0,
      limit: 10,
      ...newFilters
    });
  };

  return (
    <AdvancedFilter
      onFilterChange={handleFilterChange}
      categories={categories}
    />
  );
}
```

---

### 2. Article Annotations and Highlighting

Full-featured annotation system for highlighting and note-taking on articles.

#### Database Schema

**File**: `backend/app/models/annotation.py`

**Table**: `annotations`

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| article_id | Integer | Foreign key to articles table |
| user_id | Integer | Foreign key to users table |
| highlighted_text | Text | The text that was highlighted |
| page_number | Integer | Optional page reference for PDFs |
| position_data | JSON | Optional position metadata |
| color | String(20) | Highlight color: yellow, green, blue, red, purple |
| note | Text | User's note/comment on the highlight |
| tags | JSON | Array of tags for categorization |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Migration**: `backend/alembic/versions/add_annotations_table.py`

To apply the migration:
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

#### Backend API Endpoints

**File**: `backend/app/api/routes/annotations.py`

##### Create Annotation
```
POST /api/annotations/
```

**Request Body**:
```json
{
  "article_id": 1,
  "highlighted_text": "This is an important finding",
  "page_number": 5,
  "color": "yellow",
  "note": "Remember to cite this in my paper",
  "tags": ["important", "methods"]
}
```

##### Get Article Annotations
```
GET /api/annotations/article/{article_id}
```

**Query Parameters**:
- `color`: Filter by highlight color
- `tag`: Filter by specific tag

##### Get All My Annotations
```
GET /api/annotations/my-annotations
```

**Query Parameters**:
- `skip`, `limit`: Pagination
- `article_id`: Filter by article
- `color`: Filter by color

##### Update Annotation
```
PUT /api/annotations/{annotation_id}
```

**Request Body**: (all fields optional)
```json
{
  "color": "green",
  "note": "Updated note",
  "tags": ["important", "methods", "results"]
}
```

##### Delete Annotation
```
DELETE /api/annotations/{annotation_id}
```

##### Get Annotation Statistics
```
GET /api/annotations/article/{article_id}/stats
```

**Response**:
```json
{
  "article_id": 1,
  "total_annotations": 15,
  "color_distribution": {
    "yellow": 8,
    "green": 4,
    "blue": 2,
    "red": 1
  },
  "tags": ["important", "methods", "results"],
  "annotations_with_notes": 10
}
```

#### Frontend Implementation

**Component**: `frontend/src/components/ui/AnnotationPanel.tsx`

A comprehensive React component for managing annotations:

**Features**:
- Create new annotations with text, color, notes, and tags
- List all annotations for an article
- Filter annotations by color or tag
- Edit existing annotations
- Delete annotations
- Visual representation with color-coded highlights
- Tag management
- Page number references
- Timestamps

**Usage Example**:

```tsx
import { AnnotationPanel, Annotation } from './components/ui';
import { annotationsAPI } from './services/api';

function ArticleView({ articleId }: { articleId: number }) {
  const [annotations, setAnnotations] = useState<Annotation[]>([]);

  useEffect(() => {
    loadAnnotations();
  }, [articleId]);

  const loadAnnotations = async () => {
    const res = await annotationsAPI.getByArticle(articleId);
    setAnnotations(res.data);
  };

  const handleCreate = async (annotation: Partial<Annotation>) => {
    await annotationsAPI.create({
      ...annotation,
      article_id: articleId,
    } as any);
    loadAnnotations();
  };

  const handleUpdate = async (id: number, data: Partial<Annotation>) => {
    await annotationsAPI.update(id, data);
    loadAnnotations();
  };

  const handleDelete = async (id: number) => {
    await annotationsAPI.delete(id);
    loadAnnotations();
  };

  return (
    <AnnotationPanel
      annotations={annotations}
      onCreateAnnotation={handleCreate}
      onUpdateAnnotation={handleUpdate}
      onDeleteAnnotation={handleDelete}
    />
  );
}
```

#### API Service

**File**: `frontend/src/services/api.ts`

Added `annotationsAPI` service with full CRUD operations:

```typescript
import { annotationsAPI } from './services/api';

// Create annotation
await annotationsAPI.create({
  article_id: 1,
  highlighted_text: "Important text",
  color: "yellow",
  note: "My note"
});

// Get annotations for an article
const { data } = await annotationsAPI.getByArticle(articleId);

// Update annotation
await annotationsAPI.update(annotationId, {
  color: "green",
  note: "Updated note"
});

// Delete annotation
await annotationsAPI.delete(annotationId);

// Get statistics
const { data: stats } = await annotationsAPI.getStats(articleId);
```

---

## Color Coding System

The annotation system supports 5 colors, each with semantic meaning:

| Color | Use Case |
|-------|----------|
| Yellow | General highlights |
| Green | Agreements, positive findings |
| Blue | Definitions, key concepts |
| Red | Disagreements, concerns, important issues |
| Purple | Questions, areas needing further research |

---

## Testing

### Backend Tests

To test the new endpoints:

```bash
cd backend
source venv/bin/activate

# Test advanced filtering
curl -X GET "http://localhost:8000/api/articles/?keyword=machine&start_year=2020"

# Test annotation creation
curl -X POST "http://localhost:8000/api/annotations/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "article_id": 1,
    "highlighted_text": "Test highlight",
    "color": "yellow",
    "note": "Test note"
  }'
```

### Frontend Usage

1. **Advanced Filtering**:
   - Import and use `AdvancedFilter` component in any article list page
   - Pass `onFilterChange` callback to handle filter updates
   - Optionally provide categories for category filtering

2. **Annotations**:
   - Import and use `AnnotationPanel` component in article detail pages
   - Provide CRUD callbacks for managing annotations
   - Set `readOnly={true}` for view-only mode

---

## Database Migration

Before using the annotation features, run the database migration:

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

This will create the `annotations` table with all necessary indexes and foreign key constraints.

---

## Future Enhancements

Potential improvements for future phases:

1. **PDF Integration**: Direct highlighting in PDF viewer
2. **Collaborative Annotations**: Share annotations with other users
3. **Export Annotations**: Export to various formats (PDF, Markdown, etc.)
4. **Smart Search**: Search within annotations
5. **Annotation Templates**: Pre-defined annotation categories for different research types
6. **Rich Text Notes**: Support for formatted text in notes
7. **Attachment Support**: Attach images or files to annotations

---

## API Documentation

Full interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Navigate to the "annotations" section to explore all annotation endpoints.

---

## Support

For issues or questions about these features, please refer to:
- API documentation: `http://localhost:8000/docs`
- Project README: `/README.md`
- Phase 2 Commands Reference: `/CLAUDE.md`
