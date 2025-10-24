# 🚀 Running SIGRAA Project

## Quick Start (Recommended)

```bash
./start.sh
```

This single command will:
1. ✓ Clean up ports 8000 and 5173 (kill any existing processes)
2. ✓ Start the PostgreSQL backend on http://localhost:8000
3. ✓ Start the React frontend on http://localhost:5173
4. ✓ Check both services are running
5. ✓ Display URLs and log file locations

## Opening in Browser

Once the script shows **"✅ SIGRAA Project is Running!"**:

- **Frontend**: Open http://localhost:5173 in your browser
- **Backend API Docs**: Open http://localhost:8000/docs (Swagger UI)

## Stopping Services

```bash
./stop.sh
```

Or press **Ctrl+C** in the terminal running `start.sh`

## Logs

While running, logs are saved to:
- Backend log: `./backend.log`
- Frontend log: `./frontend.log`

## Manual Setup (If Script Fails)

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

## Troubleshooting

**Port 8000 already in use?**
```bash
kill -9 $(lsof -t -i :8000)
```

**Port 5173 already in use?**
```bash
kill -9 $(lsof -t -i :5173)
```

**Backend won't start?**
- Check Python venv: `source backend/venv/bin/activate`
- Check dependencies: `pip install -r backend/requirements.txt`

**Frontend won't start?**
- Check Node: `node --version` (should be 16+)
- Check npm: `npm install` in frontend folder

---

**See CLAUDE.md for detailed commands and troubleshooting**
