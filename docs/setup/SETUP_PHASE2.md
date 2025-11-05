# SIGRAA - Phase 2 Setup Guide

## PostgreSQL Installation (macOS)

### Option 1: Using Homebrew (Recommended)
```bash
# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Verify installation
psql --version
```

### Option 2: Using Docker
```bash
docker run --name sigraa-postgres \
  -e POSTGRES_USER=sigraa_user \
  -e POSTGRES_PASSWORD=sigraa_password \
  -e POSTGRES_DB=sigraa_db \
  -p 5432:5432 \
  -d postgres:15
```

## Step 1: Setup Database

```bash
# Create database user
createuser -P sigraa_user  # Password: sigraa_password

# Create database
createdb -O sigraa_user sigraa_db

# Verify connection
psql -U sigraa_user -d sigraa_db -c "SELECT 1;"
```

## Step 2: Setup Backend Environment

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Verify .env has correct DATABASE_URL
# DATABASE_URL=postgresql://sigraa_user:sigraa_password@localhost:5432/sigraa_db
```

## Step 3: Initialize Alembic

```bash
cd backend

# Initialize Alembic (if not already done)
alembic init -t async alembic

# The script will guide you through setup
```

## Step 4: Create Initial Migration

```bash
cd backend

# Generate migration from models
alembic revision --autogenerate -m "Initial migration"

# Review generated migration in alembic/versions/

# Apply migration to database
alembic upgrade head
```

## Step 5: Verify Database

```bash
# Connect to database and verify tables
psql -U sigraa_user -d sigraa_db

# List tables
\dt

# Check schema
\d users

# Exit
\q
```

## Step 6: Install Frontend Dependencies

```bash
cd frontend

# Install packages
npm install

# Copy environment file
cp .env.example .env
```

## Step 7: Run Backend Tests

```bash
cd backend

# Run pytest
pytest -v

# Run with coverage
pytest --cov=app tests/
```

## Step 8: Run Frontend Tests

```bash
cd frontend

# Install test dependencies
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom

# Run tests
npm run test
```

## Quick Start Commands

### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
# Frontend available at http://localhost:5173
```

### Terminal 3 - Database (if using Docker)
```bash
docker logs -f sigraa-postgres
```

## Troubleshooting

### Connection Refused
```bash
# Check PostgreSQL is running
brew services list

# If not running
brew services start postgresql@15
```

### Database Already Exists
```bash
# Drop and recreate
dropdb -U sigraa_user sigraa_db
createdb -O sigraa_user sigraa_db
```

### Permission Denied on alembic
```bash
# Make migration scripts executable
chmod +x alembic/versions/*.py
```

### Import Errors in Backend
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

1. ✅ Install PostgreSQL
2. ✅ Create database and user
3. ✅ Setup backend environment
4. ✅ Initialize and run migrations
5. ✅ Install frontend dependencies
6. 🔄 Run backend tests
7. 🔄 Run frontend tests
8. 🔄 API integration tests

## Database Schema

All 5 models will be created automatically:
- `users` - User accounts
- `articles` - PDF documents
- `categories` - Article categories
- `user_libraries` - Personal collections
- `recommendations` - Article suggestions

## Environment Files

Backend (.env):
- DATABASE_URL - PostgreSQL connection string
- SECRET_KEY - JWT secret (change in production!)
- CORS_ORIGINS - Allowed frontend origins

Frontend (.env):
- VITE_API_URL - Backend API endpoint

---

For detailed documentation, see:
- IMPLEMENTATION_SUMMARY.md - Architecture overview
- GETTING_STARTED.md - Initial setup guide
- ROADMAP.md - 16-week plan
