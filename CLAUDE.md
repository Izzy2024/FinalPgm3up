# SIGRAA - Phase 2 Commands Reference

## 🚀 Quick Start (One Command!)

### Start Full Project (Backend + Frontend)
```bash
./start.sh
```

This will:
- Clean up ports 8000 and 5173
- Start PostgreSQL backend on http://localhost:8000
- Start React frontend on http://localhost:5173
- Show real-time logs for both services
- Monitor startup health

### Stop All Services
```bash
./stop.sh
```

---

## Backend Setup & Testing

### Initial Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Database Management
```bash
# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head

# View migration history
alembic history

# Downgrade database
alembic downgrade -1

# Drop all tables and recreate
alembic downgrade base
alembic upgrade head
```

### Testing
```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_auth.py -v

# Run tests with coverage
pytest --cov=app tests/

# Run tests in watch mode (with pytest-watch)
ptw

# Run specific test
pytest tests/test_auth.py::test_login_endpoint -v

# Show print statements in tests
pytest -s

# Run tests in parallel (with pytest-xdist)
pytest -n auto
```

### Code Quality
```bash
# Format code with black
black app/ tests/

# Check code style with flake8
flake8 app/ tests/

# Sort imports with isort
isort app/ tests/

# Type check with mypy
mypy app/

# Run all checks
black app/ tests/ && isort app/ tests/ && flake8 app/ tests/ && mypy app/
```

### Running the Server
```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000

# With custom workers
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

---

## Frontend Setup & Testing

### Initial Setup
```bash
cd frontend
npm install
cp .env.example .env
```

### Development
```bash
# Start dev server
npm run dev

# Build for production
npm build

# Preview production build
npm run preview
```

### Testing
```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test -- --watch

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm run test -- src/tests/authStore.test.ts

# Run tests matching pattern
npm run test -- --grep "Auth"
```

### Code Quality
```bash
# Check TypeScript types
npm run type-check

# Run ESLint
npm run lint

# Format with prettier (if configured)
npm run format

# All checks
npm run type-check && npm run lint && npm run test
```

---

## Full Application Startup

### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

### Terminal 3 - Database (optional, if using Docker)
```bash
docker ps  # Check PostgreSQL container
docker logs sigraa-postgres  # View logs
```

---

## Database Commands

### PostgreSQL CLI
```bash
# Connect to database
psql -U sigraa_user -d sigraa_db

# Common commands inside psql:
\dt              # List all tables
\d users         # Describe table schema
\q               # Quit

# Run SQL command from CLI
psql -U sigraa_user -d sigraa_db -c "SELECT * FROM users;"

# Export data
psql -U sigraa_user -d sigraa_db -c "COPY users TO STDOUT;" > users.csv

# Import data
psql -U sigraa_user -d sigraa_db -c "COPY users FROM STDIN;" < users.csv
```

### Database Reset
```bash
# Drop all data (keep schema)
psql -U sigraa_user -d sigraa_db -c "
  DELETE FROM recommendations;
  DELETE FROM user_libraries;
  DELETE FROM articles;
  DELETE FROM categories;
  DELETE FROM users;
"

# Drop database and recreate
dropdb -U sigraa_user sigraa_db
createdb -O sigraa_user sigraa_db
alembic upgrade head
```

---

## API Testing

### Using cURL
```bash
# Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=testuser&password=password123'

# Get current user
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get articles
curl -X GET http://localhost:8000/api/articles \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Using Postman/Insomnia
1. Set base URL: `http://localhost:8000`
2. Set auth type to Bearer Token for protected endpoints
3. Import environment variables for easier management

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Debugging

### Backend
```bash
# Enable SQLAlchemy query logging
# In .env set: SQLALCHEMY_ECHO=True

# Debug mode
DEBUG=True in .env

# Print statements in tests
pytest -s tests/test_file.py
```

### Frontend
```bash
# React Developer Tools
# Install Chrome/Firefox extension

# Vue/React DevTools for state
# Check zustand store with browser console:
# import { useAuthStore } from './context/authStore'
# useAuthStore.getState()

# Network debugging
# Open DevTools -> Network tab
```

---

## Git Commands

```bash
# Stage changes
git add .

# Commit changes
git commit -m "feat: description"

# Pull latest
git pull origin main

# Push changes
git push origin feature-branch

# View status
git status

# View logs
git log --oneline -10
```

---

## Common Issues & Solutions

### Issue: "Connection refused" on database
**Solution**: 
```bash
brew services start postgresql@15
# or
docker start sigraa-postgres
```

### Issue: "Module not found" in Python
**Solution**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "CORS error" in frontend
**Solution**: Ensure CORS_ORIGINS in backend .env includes frontend URL
```
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Issue: Port already in use
**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 PID

# Or use different port
uvicorn app.main:app --reload --port 8001
```

---

## Performance Monitoring

### Backend
```bash
# Profile with cProfile
python -m cProfile -o output.prof -m uvicorn app.main:app

# Analyze with snakeviz
snakeviz output.prof
```

### Frontend
```bash
# Analyze bundle size
npm run build -- --stats

# View component render performance
# Use React DevTools Profiler
```

---

## Deployment Checklist

- [ ] Run all tests and ensure they pass
- [ ] Run linting and formatting
- [ ] Check for security vulnerabilities
- [ ] Update version numbers
- [ ] Update changelog
- [ ] Create release notes
- [ ] Build Docker images
- [ ] Deploy to staging
- [ ] Run integration tests
- [ ] Deploy to production

---

**Last updated**: October 24, 2025
**Status**: Phase 2 - Database & Testing Setup
