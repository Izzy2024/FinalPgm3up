# SIGRAA - Development Roadmap

## Overview
Sistema de Gestión y Recomendación de Artículos Académicos (SIGRAA) - A comprehensive platform for managing, classifying, and receiving recommendations for academic articles.

## Development Timeline

### Phase 1: Setup & Foundations (Weeks 1-3) ✅ IN PROGRESS
- [x] Configure development environment
- [x] Create project structure
- [x] Database models design
- [x] Backend setup (FastAPI)
- [ ] Database setup (PostgreSQL)
- [ ] Frontend setup (React)

### Phase 2: Core Functionality (Weeks 4-8)
- [ ] PDF metadata extraction
- [ ] Article classification system
- [ ] User library management
- [ ] Recommendation engine
- [ ] Bibliography generators (APA, MLA, Chicago)

### Phase 3: Advanced Features (Weeks 9-12)
- [ ] Advanced search functionality
- [ ] Dashboard with analytics
- [ ] External API integration (CrossRef, arXiv)
- [ ] Collaborative features

### Phase 4: Optimization & Deployment (Weeks 13-16)
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Production deployment

## Current Status

### Backend
- ✅ Project structure created
- ✅ Database models defined
- ✅ FastAPI application setup
- ✅ JWT authentication implemented
- ✅ Core services created:
  - PDF metadata extractor
  - Article classifier
  - Recommendation engine
  - Bibliography generator
- ✅ API routes created:
  - Authentication (register, login, me)
  - Users (get, update profile)
  - Articles (CRUD, upload)
  - Recommendations (get)

### Frontend
- ✅ React + TypeScript setup
- ✅ Vite configuration
- ✅ Tailwind CSS setup
- ✅ Router configuration
- ✅ Pages created:
  - Login
  - Register
  - Dashboard
  - Library
  - Upload
  - Recommendations
- ✅ API service layer
- ✅ Auth store (Zustand)

### Database
- ✅ Schema designed
- [ ] PostgreSQL instance setup
- [ ] Alembic migrations configured

## Next Steps

1. **Setup PostgreSQL Database**
   ```bash
   # Install PostgreSQL if not installed
   # Create database: sigraa_db
   # Run migrations: alembic upgrade head
   ```

2. **Install Backend Dependencies**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   ```

4. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run Development Servers**
   ```bash
   # Terminal 1 - Backend
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

## Architecture Overview

### Backend Architecture
```
FastAPI Application
├── Core (Config, Database, Security, Schemas)
├── Models (SQLAlchemy ORM)
├── Services (Business Logic)
│   ├── metadata_extractor
│   ├── classifier
│   ├── recommender
│   └── bibliography_generator
└── API (Routes)
    ├── auth
    ├── users
    ├── articles
    └── recommendations
```

### Database Schema
- Users
- Articles
- Categories
- UserLibrary (Personal collections)
- Recommendations
- UserSessions (Future)

### Frontend Structure
```
React App
├── Pages (Login, Register, Dashboard, etc.)
├── Components (Reusable UI components)
├── Services (API calls)
├── Context (State management with Zustand)
└── Hooks (Custom React hooks)
```

## Key Features to Implement

### MVP (Minimum Viable Product)
- [x] User authentication
- [x] Article upload
- [ ] PDF metadata extraction
- [ ] Article classification
- [ ] Basic recommendations
- [x] Library management
- [x] Bibliography generation

### Enhancements
- [ ] Advanced search
- [ ] Collaborative sharing
- [ ] Analytics dashboard
- [ ] Mobile responsive design
- [ ] Offline support

## Technology Stack

### Backend
- Python 3.9+
- FastAPI
- PostgreSQL
- SQLAlchemy
- PyPDF2 / pdfplumber
- scikit-learn

### Frontend
- React 18
- TypeScript
- Vite
- Tailwind CSS
- React Router
- React Query
- Zustand

## Deployment

### Development
```bash
# Backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
npm run dev
```

### Production
- Docker containerization
- AWS/Heroku deployment
- PostgreSQL cloud hosting
- CDN for static assets

## Testing Strategy

### Backend
- Unit tests (pytest)
- Integration tests
- API endpoint tests

### Frontend
- Component tests (Vitest)
- Integration tests (React Testing Library)
- E2E tests (Playwright/Cypress - Future)

## Documentation

- API documentation (FastAPI auto-docs)
- User manual
- Developer guide
- Deployment guide

## Team & Contributions

- Full stack implementation by single developer
- Open to contributions and improvements
- Follow PEP 8 (Python) and ESLint (JavaScript)

## Feedback & Iterations

User feedback will be collected and incorporated iteratively:
1. Collect feedback from early users
2. Analyze usage patterns
3. Implement improvements
4. Release updates

---

Last Updated: 2024
Status: In Development (Phase 1)
