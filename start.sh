#!/bin/bash

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PORT=8000
FRONTEND_PORT=5173
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "🚀 SIGRAA Project Startup Script"
echo "=================================="

cleanup_ports() {
    echo "🧹 Cleaning up ports..."
    
    if lsof -i :$BACKEND_PORT &>/dev/null; then
        echo "   Killing process on port $BACKEND_PORT..."
        kill -9 $(lsof -t -i :$BACKEND_PORT) 2>/dev/null || true
        sleep 1
    fi
    
    if lsof -i :$FRONTEND_PORT &>/dev/null; then
        echo "   Killing process on port $FRONTEND_PORT..."
        kill -9 $(lsof -t -i :$FRONTEND_PORT) 2>/dev/null || true
        sleep 1
    fi
    
    echo "   ✓ Ports cleaned"
}

check_backend_ready() {
    local count=0
    while [ $count -lt 30 ]; do
        if curl -s http://localhost:$BACKEND_PORT/docs > /dev/null; then
            echo "   ✓ Backend is ready"
            return 0
        fi
        count=$((count + 1))
        sleep 1
    done
    echo "   ⚠ Backend startup timeout"
    return 1
}

check_frontend_ready() {
    local count=0
    while [ $count -lt 30 ]; do
        if curl -s http://localhost:$FRONTEND_PORT > /dev/null; then
            echo "   ✓ Frontend is ready"
            return 0
        fi
        count=$((count + 1))
        sleep 1
    done
    echo "   ⚠ Frontend startup timeout"
    return 1
}

cleanup_ports

echo ""
echo "📁 Starting Backend..."
echo "   Location: $BACKEND_DIR"

cd "$BACKEND_DIR"

if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi

if [ ! -f ".env" ]; then
    echo "   Creating .env file from template..."
    cp .env.example .env 2>/dev/null || echo "   (No .env.example found)"
fi

source venv/bin/activate

echo "   Starting uvicorn server on port $BACKEND_PORT..."
uvicorn app.main:app --reload --port $BACKEND_PORT > "$PROJECT_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

sleep 2
check_backend_ready

echo ""
echo "📁 Starting Frontend..."
echo "   Location: $FRONTEND_DIR"

cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
    echo "   Installing dependencies..."
    npm install
fi

if [ ! -f ".env" ]; then
    echo "   Creating .env file from template..."
    cp .env.example .env 2>/dev/null || echo "   (No .env.example found)"
fi

echo "   Starting dev server on port $FRONTEND_PORT..."
npm run dev > "$PROJECT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

sleep 3
check_frontend_ready

echo ""
echo "=================================="
echo "✅ SIGRAA Project is Running!"
echo "=================================="
echo ""
echo "📍 URLs:"
echo "   Frontend:  http://localhost:$FRONTEND_PORT"
echo "   Backend:   http://localhost:$BACKEND_PORT"
echo "   Docs:      http://localhost:$BACKEND_PORT/docs"
echo ""
echo "📋 Logs:"
echo "   Backend:  $PROJECT_DIR/backend.log"
echo "   Frontend: $PROJECT_DIR/frontend.log"
echo ""
echo "🛑 To stop both services, press Ctrl+C"
echo ""

trap 'echo ""; echo "🛑 Stopping services..."; kill $BACKEND_PID 2>/dev/null || true; kill $FRONTEND_PID 2>/dev/null || true; wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; echo "✓ Services stopped"; exit 0' INT TERM

wait
