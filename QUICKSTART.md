# Quick Start Guide

## ✅ Setup Complete!

Your AI Trainer is ready to run. Here's how to start:

## 🚀 Starting the App

```bash
cd /home/vishnu/ai/ai_trainer
./scripts/dev.sh
```

This will start:
- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:5173

## 📱 Using the App

1. Open your browser: http://localhost:5173
2. You'll see the Home screen with today's stats
3. Click "Start Workout" or navigate to "Exercises"
4. Select an exercise (e.g., Squats)
5. Allow webcam access when prompted
6. Follow the on-screen feedback

## 🛑 Stopping the Servers

Press `Ctrl+C` in the terminal where dev.sh is running

## 🔍 Troubleshooting

### If backend fails to start:
```bash
source .venv/bin/activate
python startup_backend.py
# Check error messages
```

### If frontend fails:
```bash
npm run dev
# Check error messages
```

### If dependencies are missing:
```bash
# Python
source .venv/bin/activate
pip install -r requirements.txt

# Node
npm install
```

### Clean rebuild:
```bash
rm -rf .venv node_modules
python3.10 scripts/setup_venv.py
npm install
```

## 📊 API Documentation

Once backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🎯 Available Endpoints

### REST API
- `GET /api/exercises` - List exercises
- `GET /api/stats/today` - Today's stats
- `GET /api/stats/weekly` - Weekly stats
- `POST /api/workouts` - Save workout

### WebSocket
- `WS /ws/workout?exercise=squat` - Live pose detection stream

## 📝 Notes

- Webcam is accessed by Python backend (not browser)
- Works best on Chrome/Edge browsers
- Requires Python 3.10 for MediaPipe compatibility
- First run initializes SQLite database at `data/fitness.db`

## 🚧 Current Status

**Working:**
- ✅ Home screen with stats
- ✅ Exercise list
- ✅ Backend API
- ✅ Database setup
- ✅ Navigation

**In Progress (Phase 2):**
- 🔄 Live workout screen with video
- 🔄 WebSocket video streaming
- 🔄 Real-time rep counting in browser
- 🔄 Progress tracking charts

---

Happy training! 💪

