#!/bin/bash

echo "Testing AI Trainer Setup..."
echo ""

cd /home/vishnu/ai/ai_trainer

# Test 1: Virtual environment
echo "1. Checking virtual environment..."
if [ -d ".venv" ]; then
    echo "   ✅ .venv exists"
    source .venv/bin/activate
    python_version=$(python --version 2>&1)
    echo "   ✅ Python: $python_version"
else
    echo "   ❌ .venv not found"
    exit 1
fi

# Test 2: Python dependencies
echo ""
echo "2. Checking Python dependencies..."
python -c "import fastapi; import uvicorn; import sqlalchemy; print('   ✅ FastAPI, Uvicorn, SQLAlchemy installed')" 2>/dev/null || echo "   ❌ Missing Python dependencies"
python -c "import cv2; import mediapipe; print('   ✅ OpenCV, MediaPipe installed')" 2>/dev/null || echo "   ❌ Missing CV dependencies"

# Test 3: Node modules
echo ""
echo "3. Checking Node dependencies..."
if [ -d "node_modules" ]; then
    echo "   ✅ node_modules exists"
else
    echo "   ❌ node_modules not found"
fi

# Test 4: Backend imports
echo ""
echo "4. Testing backend imports..."
python startup_backend.py &
BACKEND_PID=$!
sleep 3
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "   ✅ Backend API responding"
    kill $BACKEND_PID 2>/dev/null
else
    echo "   ❌ Backend not responding"
    kill $BACKEND_PID 2>/dev/null
fi

# Test 5: Frontend build
echo ""
echo "5. Testing frontend..."
if [ -f "package.json" ]; then
    echo "   ✅ package.json exists"
else
    echo "   ❌ package.json not found"
fi

echo ""
echo "Setup test complete!"
echo ""
echo "To start development servers:"
echo "  ./scripts/dev.sh"

