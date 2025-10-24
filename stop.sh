#!/bin/bash

echo "🛑 Stopping SIGRAA Services..."
echo ""

pkill -f "uvicorn app.main" 2>/dev/null && echo "✓ Backend stopped" || echo "✓ Backend not running"
pkill -f "npm run dev" 2>/dev/null && echo "✓ Frontend stopped" || echo "✓ Frontend not running"
pkill -f "vite" 2>/dev/null && echo "✓ Vite stopped" || echo "✓ Vite not running"

sleep 1

if ! lsof -i :8000 &>/dev/null && ! lsof -i :5173 &>/dev/null; then
    echo ""
    echo "✅ All services stopped successfully"
else
    echo ""
    echo "⚠ Some services may still be running"
    echo "Try killing manually:"
    echo "  kill -9 \$(lsof -t -i :8000)"
    echo "  kill -9 \$(lsof -t -i :5173)"
fi
