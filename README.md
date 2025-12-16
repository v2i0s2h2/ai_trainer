# AI Trainer - Real-time Pose Detection & Workout Tracking

A full-stack fitness application with real-time pose detection, rep counting, and form correction using MediaPipe, FastAPI, and SvelteKit.

## 🎯 Features

- ✅ Real-time pose detection using MediaPipe
- ✅ Automatic rep counting with hysteresis
- ✅ Live form corrections and feedback
- ✅ WebSocket video streaming
- ✅ Workout history and statistics
- ✅ Modern, mobile-responsive UI
- 🔄 Voice feedback (Hinglish support)
- 🔄 Progress tracking and achievements
- 🔄 Multiple exercise types

## 🏗️ Architecture


### Monorepo Structure
```
ai_trainer/
├── src/
│   ├── backend/          # Python FastAPI backend
│   │   ├── api/          # REST & WebSocket endpoints
│   │   ├── core/         # Voice feedback, analyzers
│   │   ├── exercises/    # Exercise trainers (squat, glute_fly)
│   │   ├── database/     # SQLite models
│   │   └── main.py       # FastAPI app
│   └── frontend/         # SvelteKit app
│       └── src/
│           ├── lib/      # Components, stores, API client
│           └── routes/   # Pages (Home, Exercises, Progress, Profile)
├── scripts/
│   ├── dev.sh            # Start both servers
│   ├── run.py            # CLI trainer (legacy)
│   └── setup_venv.py     # Environment setup
└── data/                 # SQLite database
```

### Tech Stack

**Backend:**
- Python 3.10
- FastAPI + Uvicorn (WebSocket support)
- MediaPipe (pose detection)
- OpenCV (video processing)
- SQLAlchemy + SQLite
- gTTS + pygame (voice feedback)

**Frontend:**
- SvelteKit 5
- Tailwind CSS 4
- TypeScript
- Vite

## 🚀 Quick Start

### Prerequisites

- Python 3.10 (required for MediaPipe compatibility)
- Node.js 18+ and npm
- Webcam

### Installation

1. **Clone and setup:**
```bash
git clone <repo-url>
cd ai_trainer
```

2. **Install dependencies:**
```bash
# Python dependencies (creates .venv automatically)
python scripts/setup_venv.py

# Node dependencies
npm install
```

3. **Run development servers:**
```bash
./scripts/dev.sh
```

This starts:
- Backend API: http://localhost:8001
- Frontend: http://localhost:5173

## 📱 Usage

### Web App (Recommended)

1. Open http://localhost:5173 in your browser
2. Click "Start Workout"
3. Select an exercise (e.g., Squats)
4. Allow webcam access
5. Follow on-screen instructions and feedback

> **Camera tip:** Full-body tracking works best on a laptop or desktop with a wide webcam (or USB camera) placed a few meters away. Mobile phones rarely capture the entire pose, so rep counting and form feedback may be unreliable on mobile.

### CLI (Legacy)

```bash
# Activate venv
source .venv/bin/activate

# Run squat trainer
./scripts/run.py squat

# Run glute fly trainer
./scripts/run.py
```

## 🎨 UI Screens

- **Home**: Welcome, quick stats, Start Workout CTA
- **Exercises**: Library of available exercises with filters
- **Workout**: Live video feed with pose detection, rep counter, feedback
- **Progress**: Weekly stats, achievements, workout calendar
- **Profile**: User stats, settings

## 🔌 API Endpoints

### REST API

```
GET  /api/exercises           # List all exercises
GET  /api/exercises/{id}      # Get exercise details
GET  /api/stats/today         # Today's workout stats
GET  /api/stats/weekly        # Weekly statistics
POST /api/workouts            # Save completed workout
GET  /api/achievements        # User achievements
```

### WebSocket

```
WS /ws/workout?exercise=squat
```

**Message format:**
```json
{
  "type": "frame",
  "image": "data:image/jpeg;base64,...",
  "reps": 5,
  "feedback": "Good form - keep going!",
  "angles": { "knee": 85.3, "torso": 72.1 },
  "progress": 0.75
}
```

## 🛠️ Development

### Project Structure

```
src/backend/
├── main.py                 # FastAPI app entry
├── api/
│   ├── routes.py           # REST endpoints
│   └── websocket.py        # WebSocket handler
├── exercises/
│   ├── squat_trainer.py    # Squat detection logic
│   └── glute_fly.py        # Glute fly logic
└── database/
    ├── db.py               # SQLAlchemy setup
    └── models.py           # Database models

src/frontend/src/
├── routes/
│   ├── +layout.svelte      # Root layout + bottom nav
│   ├── +page.svelte        # Home page
│   ├── exercises/
│   ├── progress/
│   └── profile/
└── lib/
    ├── components/         # Reusable UI components
    ├── stores/             # Svelte stores (state)
    └── api/                # API client functions
```

### Adding a New Exercise

1. **Create trainer class:**
```python
# src/backend/exercises/pushup_trainer.py
class PushupTrainer:
    def process_frame(self, results, w, h):
        # Your pose detection logic
        return {
            "reps": self.reps,
            "feedback": "...",
            "angles": {...},
            "progress": 0.0
        }
```

2. **Register in WebSocket handler:**
```python
# src/backend/api/websocket.py
def get_trainer(self):
    if self.exercise == "pushup":
        return PushupTrainer()
```

3. **Add to exercises list:**
```python
# src/backend/api/routes.py
EXERCISES.append({
    "id": "pushup",
    "name": "Push-ups",
    "category": "chest",
    ...
})
```

### Color Palette

```css
--bg-primary: #0A1628      /* Deep navy */
--bg-card: #1E293B         /* Dark slate */
--primary: #3B82F6         /* Blue */
--accent-orange: #F97316
--accent-purple: #A855F7  
--accent-green: #10B981
--text-primary: #FFFFFF
--text-secondary: #94A3B8
```

## 🧪 Testing

```bash
# Python backend
source .venv/bin/activate
pytest tests/

# Frontend (when implemented)
npm run test
```

## 📦 Building for Production

```bash
# Build frontend
npm run build

# Backend runs with uvicorn in production mode
uvicorn src.backend.main:app --host 0.0.0.0 --port 8000
```

## 🐛 Troubleshooting

### Webcam Issues
- Ensure browser has camera permissions
- Check if another app is using the webcam
- Try different browsers (Chrome/Edge recommended)

### MediaPipe Installation
- Requires Python 3.10 (not 3.11 or 3.12)
- On Arch Linux: `sudo pacman -S python310`
- Recreate venv: `rm -rf .venv && python3.10 scripts/setup_venv.py`

### Voice Feedback Not Working
- Install audio backends: `sudo pacman -S espeak-ng sdl2_mixer`
- Check audio output device settings
- Voice feedback auto-falls back to pyttsx3 if gTTS fails

## 📄 License

MIT License - See LICENSE file

## 🤝 Contributing

1. Fork the repo
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 🎯 Roadmap

- [x] Phase 1: Monorepo setup + FastAPI backend
- [ ] Phase 2: Live workout screen with WebSocket
- [ ] Phase 3: Progress tracking & achievements
- [ ] Phase 4: Video tutorials
- [ ] Phase 5: Social features & sharing
- [ ] Phase 6: Mobile app (React Native)

---

Made with 💪 by AI Trainer Team

                      ┌─────────────────────────────┐
                      │     Frontend (Svelte)        │
                      │  (Cloudflare / Localhost)    │
                      └──────────────┬──────────────┘
                                     │ HTTP / WS
                                     ▼
                     ┌──────────────────────────────────┐
                     │        main.py (Boss File)        │
                     │ - FastAPI() init                  │
                     │ - CORS setup                      │
                     │ - Routers include                 │
                     └───────────┬─────────┬───────────┘
                                 │         │
                     ┌───────────▼───┐   ┌─▼────────────────┐
                     │ routes.py     │   │ websocket.py      │
                     │ (REST APIs)   │   │ (Live WebSocket)  │
                     └──────┬────────┘   └────────┬─────────┘
                            │                     │
          ┌─────────────────┴─────────────────────┴───────────────┐
          │                                                        │
 ┌────────▼────────┐                                   ┌──────────▼────────┐
 │ models.py       │                                   │ security.py        │
 │ (Pydantic + DB  │                                   │ (Auth + JWT)       │
 │  Models)        │                                   │                    │
 └────────┬────────┘                                   └──────────┬─────────┘
          │                                                        │
          ▼                                                        ▼
 ┌──────────────────┐                                ┌────────────────────────┐
 │ core/             │                                │ Database (SQLite/Postgres)│
 │ - exercise_analyzer.py                            │ via ORM (SQLAlchemy)   │
 │ - pose_processor.py                                └────────────────────────┘
 │ - voice_feedback.py
 └──────────────────┘
