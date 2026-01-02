#!/bin/bash

# AI Trainer Backend Server

echo "🚀 Starting AI Trainer Backend"
echo ""

# Colors for output
GREEN='
'
BLUE='
'
NC='
' # No Color

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "⚠️  Virtual environment not found. Running setup..."
    python3 scripts/setup_venv.py
fi

# Activate virtual environment
source .venv/bin/activate

# Initialize database
echo "💾 Initializing database..."
python3 -c "from src.backend.database.db import init_db; init_db()"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Starting server:"
echo "  📡 Backend API: http://localhost:8001"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping server..."
    kill $BACKEND_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM

# Start backend
echo "[Backend] Starting FastAPI server..."
python3 startup_backend.py &
BACKEND_PID=$!

wait $BACKEND_PID
