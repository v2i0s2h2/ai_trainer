#!/bin/bash

# AI Trainer Development Server
# Starts both FastAPI backend and SvelteKit frontend

echo "🚀 Starting AI Trainer Development Environment"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "⚠️  Virtual environment not found. Running setup..."
    python scripts/setup_venv.py
fi

# Activate virtual environment
source .venv/bin/activate

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

# Initialize database
echo "💾 Initializing database..."
python -c "from src.backend.database.db import init_db; init_db()"

echo ""
echo "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "${BLUE}Starting servers:${NC}"
echo "  📡 Backend API: http://localhost:8000"
echo "  🌐 Frontend:   http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

trap cleanup INT TERM

# Start backend in background
echo "${BLUE}[Backend]${NC} Starting FastAPI server..."
python startup_backend.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend
echo "${BLUE}[Frontend]${NC} Starting Vite dev server..."
npm run dev -- --host &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID

