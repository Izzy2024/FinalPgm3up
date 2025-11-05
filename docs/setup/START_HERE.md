# 🚀 Phase 2 - Getting Started NOW

## What Just Happened

Phase 2 infrastructure has been completely set up! You now have:

✅ **Database Migration System** (Alembic)
✅ **Backend Test Suite** (pytest) - 16 test cases
✅ **Frontend Test Suite** (Vitest) - 9 test cases  
✅ **Automated Setup Script**
✅ **Complete Documentation** (CLAUDE.md)

---

## Step 1: Install PostgreSQL (5 minutes)

### macOS with Homebrew (Recommended)
```bash
# Install PostgreSQL 15
brew install postgresql@15

# Start the service
brew services start postgresql@15

# Verify it's running
psql --version
```

### Alternative: Docker
```bash
docker run --name sigraa-postgres \
  -e POSTGRES_USER=sigraa_user \
  -e POSTGRES_PASSWORD=sigraa_password \
  -e POSTGRES_DB=sigraa_db \
  -p 5432:5432 \
  -d postgres:15
```

---

## Step 2: Run Automated Setup (3 minutes)

```bash
cd /Users/admin/Documents/UP/proyectofinal

# Run the setup script
./setup_phase2.sh
```

**What this does:**
- ✅ Verifies PostgreSQL is running
- ✅ Creates Python virtual environment
- ✅ Installs backend dependencies
- ✅ Installs frontend dependencies
- ✅ Creates database tables with Alembic
- ✅ Sets up .env files

---

## Step 3: Verify Everything Works (2 minutes)

### Test Database Connection
```bash
psql -U sigraa_user -d sigraa_db -c "\dt"
```

Should show 5 tables:
- users
- articles  
- categories
- user_libraries
- recommendations

### Run Backend Tests
```bash
cd backend
source venv/bin/activate
pytest -v
```

Expected output: **16 tests passed**

### Run Frontend Tests
```bash
cd frontend
npm run test
```

Expected output: **9 tests passed**

---

## Step 4: Start Development (Ongoing)

### Terminal 1 - Backend API
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

API available at: **http://localhost:8000**
Swagger Docs: **http://localhost:8000/docs**

### Terminal 2 - Frontend App
```bash
cd frontend
npm run dev
```

App available at: **http://localhost:5173**

### Terminal 3 - Optional: Monitor Database
```bash
psql -U sigraa_user -d sigraa_db

# Inside psql:
SELECT * FROM users;  -- View users
\dt                   -- List all tables
\q                    -- Quit
```

---

## Common Commands

Save these for quick reference:

```bash
# Backend tests
cd backend && source venv/bin/activate && pytest -v

# Frontend tests
cd frontend && npm run test

# Database reset
psql -U sigraa_user -d sigraa_db -c "
  DELETE FROM recommendations;
  DELETE FROM user_libraries;
  DELETE FROM articles;
  DELETE FROM categories;
  DELETE FROM users;
"

# View API docs
# Open browser: http://localhost:8000/docs

# Create new migration
cd backend && alembic revision --autogenerate -m "Add field to users"

# Run migration
cd backend && alembic upgrade head
```

---

## What to Do Next

### Option 1: Learn the System (Recommended)
1. Read CLAUDE.md for all available commands
2. Review PHASE2_STATUS.md for detailed info
3. Check test files to understand test structure

### Option 2: Dive into Development
1. Start backend: Terminal 1
2. Start frontend: Terminal 2
3. Test API endpoints in Swagger UI
4. Modify code and see hot-reload work

### Option 3: Deepen Testing
1. Run tests with coverage: `pytest --cov=app`
2. Check what's being tested
3. Add more test cases as needed
4. Run frontend UI tests: `npm run test:ui`

---

## Troubleshooting

### PostgreSQL Connection Failed
```bash
# Check if running
brew services list

# Start it
brew services start postgresql@15

# Or if using Docker
docker ps  # Check if container exists
docker start sigraa-postgres
```

### Import Errors in Backend
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Port Already in Use
```bash
# Port 8000 in use?
lsof -i :8000
kill -9 <PID>

# Or use different port
uvicorn app.main:app --reload --port 8001
```

### Tests Failing
```bash
# Make sure you're in the right directory
cd backend && source venv/bin/activate

# Run with verbose output
pytest -v -s

# Run specific test
pytest tests/test_auth.py::test_login_endpoint -v
```

---

## File Reference

| File | Purpose |
|------|---------|
| CLAUDE.md | Complete command reference |
| SETUP_PHASE2.md | Detailed setup guide |
| PHASE2_STATUS.md | Full status report |
| setup_phase2.sh | Automated setup script |
| backend/tests/ | Backend test cases |
| frontend/src/tests/ | Frontend test cases |
| backend/alembic/ | Database migrations |

---

## Success Indicators

✅ You're ready when:
- [ ] PostgreSQL is installed and running
- [ ] `./setup_phase2.sh` completes without errors
- [ ] `pytest -v` shows 16 passed tests
- [ ] `npm run test` shows 9 passed tests
- [ ] Backend server starts on :8000
- [ ] Frontend server starts on :5173
- [ ] Database has 5 tables

---

## Questions?

1. **Commands**: See CLAUDE.md
2. **Setup Issues**: See SETUP_PHASE2.md
3. **Architecture**: See IMPLEMENTATION_SUMMARY.md
4. **Status**: See PHASE2_STATUS.md

---

**You're all set! 🎉**

Next: Install PostgreSQL and run `./setup_phase2.sh`

Questions? Start with CLAUDE.md - it has everything!
