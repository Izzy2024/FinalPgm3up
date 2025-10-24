#!/bin/bash

echo "======================================"
echo "SIGRAA Project Setup Script"
echo "======================================"
echo ""

echo "Setting up Backend..."
cd backend
python3 -m venv venv
echo "✓ Virtual environment created"

source venv/bin/activate
pip install -r requirements.txt
echo "✓ Backend dependencies installed"

cp .env.example .env
echo "✓ Backend .env created (configure as needed)"

cd ../frontend
npm install
echo "✓ Frontend dependencies installed"

cp .env.example .env
echo "✓ Frontend .env created"

cd ..

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Configure backend/.env (update DATABASE_URL)"
echo "2. Setup PostgreSQL database:"
echo "   createdb sigraa_db"
echo "   psql -U postgres -d sigraa_db -c 'CREATE USER sigraa_user WITH PASSWORD 'sigraa_password'; ALTER ROLE sigraa_user CREATEDB;'"
echo "3. Run migrations (if using Alembic)"
echo "4. Start backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "5. Start frontend: cd frontend && npm run dev"
echo ""
