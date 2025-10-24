# SIGRAA - Getting Started Guide

## Quick Start (5 minutes)

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 12+ (or will install)

### Step 1: Clone/Navigate to Project
```bash
cd /Users/admin/Documents/UP/proyectofinal
```

### Step 2: Run Setup Script
```bash
bash scripts/setup.sh
```

### Step 3: Configure Environment

**Backend (.env)**
```bash
cd backend
# Edit .env and set:
DATABASE_URL=postgresql://sigraa_user:sigraa_password@localhost:5432/sigraa_db
SECRET_KEY=your-secret-key-here
```

**Frontend (.env)**
```bash
cd ../frontend
# Edit .env and set:
VITE_API_URL=http://localhost:8000
```

### Step 4: Start Servers

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 5: Access Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Detailed Installation

### Backend Setup

#### 1. Create Virtual Environment
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Configure Database
```bash
# Create database (macOS with Homebrew PostgreSQL)
createdb sigraa_db

# Set up user (optional, if not exists)
psql -U postgres
# In psql:
CREATE USER sigraa_user WITH PASSWORD 'sigraa_password';
ALTER ROLE sigraa_user CREATEDB;
```

#### 4. Create .env File
```bash
cp .env.example .env
```

Edit `backend/.env`:
```env
BACKEND_PORT=8000
DATABASE_URL=postgresql://sigraa_user:sigraa_password@localhost:5432/sigraa_db
SECRET_KEY=your-super-secret-key-change-in-production
DEBUG=True
```

#### 5. Run Server
```bash
uvicorn app.main:app --reload
```

Visit: http://localhost:8000/docs for interactive API documentation

---

### Frontend Setup

#### 1. Install Node Modules
```bash
cd frontend
npm install
```

#### 2. Create .env File
```bash
cp .env.example .env
```

Edit `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
```

#### 3. Start Development Server
```bash
npm run dev
```

Visit: http://localhost:5173

---

## Project Structure

```
sigraa/
├── backend/
│   ├── app/
│   │   ├── models/           # Database models
│   │   ├── core/             # Config, DB, security
│   │   ├── services/         # Business logic
│   │   ├── api/routes/       # API endpoints
│   │   └── main.py           # FastAPI app
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/            # React pages
│   │   ├── components/       # Reusable components
│   │   ├── services/         # API calls
│   │   ├── context/          # State management
│   │   └── App.tsx
│   ├── package.json
│   └── .env.example
├── data/                     # Uploaded files
├── docs/                     # Documentation
├── ROADMAP.md               # Development roadmap
├── TRACKING.md              # Progress tracking
└── README.md
```

---

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/token` - Login (OAuth2)
- `GET /api/auth/me` - Get current user

### Articles
- `POST /api/articles/upload` - Upload PDF
- `GET /api/articles` - List articles
- `GET /api/articles/{id}` - Get article details
- `PUT /api/articles/{id}` - Update article
- `DELETE /api/articles/{id}` - Delete article

### Recommendations
- `GET /api/recommendations` - Get personalized recommendations

### Users
- `GET /api/users/{id}` - Get user profile
- `PUT /api/users/profile` - Update profile

---

## Common Commands

### Backend
```bash
# Activate virtual environment
source backend/venv/bin/activate

# Run development server (with auto-reload)
uvicorn app.main:app --reload

# Run tests
pytest

# Code formatting
black app/
isort app/

# Type checking
mypy app/
```

### Frontend
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint

# Type check
npm run type-check
```

---

## Database

### Connect to Database
```bash
psql -U sigraa_user -d sigraa_db
```

### Useful SQL Commands
```sql
-- List all tables
\dt

-- Show table structure
\d articles

-- Delete all data (caution!)
DELETE FROM articles;
TRUNCATE TABLE articles;

-- Check user permissions
\du
```

---

## Troubleshooting

### Backend Issues

**1. "Module not found" error**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**2. Database connection error**
```bash
# Check PostgreSQL is running
pg_isready

# Check credentials in .env
cat .env | grep DATABASE_URL

# Verify database exists
psql -U postgres -l
```

**3. Port 8000 already in use**
```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

### Frontend Issues

**1. "Cannot find module" error**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**2. Port 5173 already in use**
```bash
# Vite will use next available port automatically
# Or specify port:
npm run dev -- --port 3000
```

---

## Next Steps

1. ✅ Complete Setup
2. ✅ Verify Backend (http://localhost:8000/docs)
3. ✅ Verify Frontend (http://localhost:5173)
4. 📖 Read API Documentation at /docs
5. 🚀 Start building features!

---

## Support & Documentation

- **API Documentation**: http://localhost:8000/docs
- **Development Guide**: See `docs/development/`
- **Database Schema**: See `docs/database/`
- **Roadmap**: See `ROADMAP.md`
- **Progress Tracking**: See `TRACKING.md`

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

Enjoy building SIGRAA! 🚀
