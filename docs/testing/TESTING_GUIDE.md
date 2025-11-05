# SIGRAA Phase 3 - Quick Testing Guide

## Current Status: ✅ All Systems Running

**Backend**: http://localhost:8000 (API)
**Frontend**: http://localhost:5173 (React)
**API Docs**: http://localhost:8000/docs (Swagger)

---

## Quick User Flow Test

### 1. **Login**
1. Go to http://localhost:5173
2. Use existing credentials:
   - **Username**: `testuser123` or `irios`
   - **Password**: `password123`

### 2. **Upload Article**
1. Click "Upload" in sidebar
2. Choose method:
   - **File Upload**: Select a PDF or TXT file
   - **URL Upload**: Paste a journal article URL
3. After upload:
   - Classification appears with suggested category
   - 5 citation formats auto-generated

### 3. **View Library**
1. Click "Library" in sidebar
2. See all uploaded articles in table
3. **Search**: Use search bar to filter by title/author
4. **Filter**: Use dropdown to filter by status (Unread/Reading/Read)

### 4. **Article Details**
1. Click eye icon in Library table
2. View article metadata:
   - Title, authors, abstract
   - Journal, year, DOI, keywords
   - Add date and current status
3. **Actions available**:
   - Rate article (1-5 stars)
   - Change status (dropdown)
   - View citations (shows all 5 formats)
   - Delete article

### 5. **View Citations**
1. From article detail modal
2. Click "View Citation Formats" button
3. See 5 formats (APA, MLA, Chicago, BibTeX, RIS)
4. Copy any format to clipboard

### 6. **Get Recommendations**
1. Click "Recommendations" in sidebar
2. View personalized recommendations based on library
3. Each shows:
   - Article title and authors
   - Similarity score
   - Reason (keywords matched, same journal, etc.)
4. Click article to view details

### 7. **Profile**
1. Click user avatar (top right)
2. View account info
3. Logout option

---

## API Testing (cURL)

### Register New User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "Password123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=testuser123&password=password123'
```

### Get User Library
```bash
TOKEN="your_token_here"
curl -X GET http://localhost:8000/api/users/library/?skip=0&limit=10 \
  -H "Authorization: Bearer $TOKEN"
```

### Classify Article
```bash
TOKEN="your_token_here"
curl -X POST http://localhost:8000/api/articles/1/classify \
  -H "Authorization: Bearer $TOKEN"
```

### Get Bibliography Format
```bash
TOKEN="your_token_here"
curl -X GET http://localhost:8000/api/articles/1/bibliography/apa \
  -H "Authorization: Bearer $TOKEN"
```

### Get Recommendations
```bash
TOKEN="your_token_here"
curl -X GET http://localhost:8000/api/recommendations/?skip=0&limit=10 \
  -H "Authorization: Bearer $TOKEN"
```

---

## Component Testing

### Frontend Components Implemented
- ✅ `Login.tsx` - Authentication form
- ✅ `Register.tsx` - User registration
- ✅ `Upload.tsx` - File and URL upload with classification display
- ✅ `Library.tsx` - Article library with search, filter, detail view
- ✅ `Recommendations.tsx` - Personalized recommendations
- ✅ `Dashboard.tsx` - Quick statistics
- ✅ `ArticleDetailModal.tsx` - Full article metadata view
- ✅ `BibliographyModal.tsx` - Citation format viewer
- ✅ `ClassificationResult.tsx` - Classification display
- ✅ `Navigation.tsx` - Sidebar navigation
- ✅ `ProtectedRoute.tsx` - Authentication guard

### UI Components Available
- Button (primary, secondary, danger variants)
- Input (text, password, search)
- Card (flexible container)
- Badge (status indicators)
- Table (with headers, columns, body)
- Dropdown (searchable, filterable)
- Avatar (user profile)
- Progress (for confidence scores)
- Modal (for details and citations)

---

## Troubleshooting

### Backend Not Running
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process if needed
kill -9 <PID>

# Restart backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload
```

### Frontend Not Running
```bash
# Check if port 5173 is in use
lsof -i :5173

# Kill existing process if needed
kill -9 <PID>

# Restart frontend
cd frontend && npm run dev
```

### CORS Errors
- Ensure backend is running and accessible
- Check `.env` file has correct `VITE_API_URL`
- Backend should have `CORS_ORIGINS=http://localhost:5173` in `.env`

### Database Connection Issues
- Verify PostgreSQL is running
- Check `.env` has correct `DATABASE_URL`
- Run migrations: `alembic upgrade head`

---

## Performance Monitoring

### Check API Response Times
```bash
# Login response time
time curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=testuser123&password=password123'
```

### Monitor Backend Logs
- Watch the terminal where `uvicorn` is running
- Shows all API calls with status codes and response times

### Monitor Frontend Build
- Watch the terminal where `npm run dev` is running
- Shows HMR (Hot Module Replacement) updates

---

## Next Steps for Production

1. **Environment Configuration**
   - Update `.env` files with production URLs
   - Set secure JWT secret
   - Configure HTTPS

2. **Deployment**
   - Build frontend: `npm run build`
   - Set up Docker containers
   - Deploy to cloud platform (AWS, Heroku, etc.)

3. **Database**
   - Migrate to production PostgreSQL
   - Set up automated backups
   - Configure connection pooling

4. **Monitoring**
   - Set up error tracking (Sentry, etc.)
   - Configure logging
   - Set up performance monitoring

5. **Security**
   - Run dependency audit
   - Enable HTTPS/TLS
   - Set up rate limiting
   - Configure CORS properly

---

**Status**: Phase 3 Complete ✅
**Ready for**: Testing, Feedback, Production Deployment
**Date Created**: October 26, 2025

