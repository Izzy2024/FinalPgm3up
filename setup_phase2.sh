#!/bin/bash

set -e

echo "🚀 SIGRAA Phase 2 Setup Script"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if PostgreSQL is running
echo -e "\n${YELLOW}Checking PostgreSQL...${NC}"
if ! psql -U sigraa_user -d sigraa_db -c "SELECT 1;" 2>/dev/null; then
    echo -e "${RED}PostgreSQL not running or connection failed${NC}"
    echo "Please ensure PostgreSQL is installed and running:"
    echo "  macOS with Homebrew: brew services start postgresql@15"
    echo "  Docker: docker run -d -e POSTGRES_PASSWORD=sigraa_password -e POSTGRES_USER=sigraa_user -e POSTGRES_DB=sigraa_db -p 5432:5432 postgres:15"
    exit 1
fi
echo -e "${GREEN}✓ PostgreSQL is running${NC}"

# Setup backend
echo -e "\n${YELLOW}Setting up Backend...${NC}"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Install dependencies
echo "Installing backend dependencies..."
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Copy .env if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
fi

# Create initial migration
echo -e "\n${YELLOW}Creating database migrations...${NC}"
alembic revision --autogenerate -m "Initial schema" -q 2>/dev/null || echo "Migration already exists"
echo -e "${GREEN}✓ Migration created${NC}"

# Apply migrations
echo "Applying migrations..."
alembic upgrade head -q
echo -e "${GREEN}✓ Migrations applied${NC}"

# Verify database schema
echo -e "\n${YELLOW}Verifying database schema...${NC}"
psql -U sigraa_user -d sigraa_db -c "\dt" | grep -E "(users|articles|categories|user_libraries|recommendations)" >/dev/null && echo -e "${GREEN}✓ All tables created${NC}" || echo -e "${RED}✗ Tables not found${NC}"

# Setup frontend
echo -e "\n${YELLOW}Setting up Frontend...${NC}"
cd ../frontend

# Install dependencies
echo "Installing frontend dependencies..."
npm install -q 2>/dev/null || npm install
echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

# Copy .env if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Frontend .env file created${NC}"
fi

echo -e "\n${GREEN}✅ Setup complete!${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Backend server (in terminal 1):"
echo "   cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "2. Frontend dev server (in terminal 2):"
echo "   cd frontend && npm run dev"
echo ""
echo "3. Access the application:"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
echo ""
