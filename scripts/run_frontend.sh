#!/bin/bash

# AI Trainer Frontend Server

echo "🚀 Starting AI Trainer Frontend"
echo ""

# Colors for output
GREEN='
'
BLUE='
'
NC='
' # No Color

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Starting server:"
echo "  🌐 Frontend:   http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping server..."
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM

# Start frontend
echo "[Frontend] Starting Vite dev server..."
npm run dev -- --host &
FRONTEND_PID=$!

wait $FRONTEND_PID
