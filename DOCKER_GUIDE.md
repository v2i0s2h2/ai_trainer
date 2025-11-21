# Docker Guide for AI Trainer

## 📦 Overview

This Docker setup creates a **single container** that runs both the FastAPI backend and the built SvelteKit frontend together.

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│      Docker Container              │
│  ┌──────────────────────────────┐  │
│  │   FastAPI Backend (Port 8000)│  │
│  │   ├── REST API (/api/*)      │  │
│  │   ├── WebSocket (/ws/*)      │  │
│  │   └── Static Files (Frontend)│  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Built SvelteKit Frontend   │  │
│  │   (Served by FastAPI)         │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

## 📁 Files Created

1. **`Dockerfile`** - Multi-stage build:
   - Stage 1: Builds SvelteKit frontend
   - Stage 2: Sets up Python backend and copies built frontend

2. **`docker-compose.yml`** - Easy container management

3. **`.dockerignore`** - Excludes unnecessary files from build

4. **`.env.example`** - Environment variables template

## 🚀 Quick Start

### 1. Build Docker Image

```bash
docker build -t ai-trainer:latest .
```

### 2. Run with Docker Compose (Recommended)

```bash
docker-compose up -d
```

### 3. Run with Docker directly

```bash
docker run -d \
  --name ai-trainer \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  ai-trainer:latest
```

## 🔧 Development vs Production

### Development Mode

For development, continue using `./scripts/dev.sh` which runs:
- Backend on `http://localhost:8000`
- Frontend dev server on `http://localhost:5173`

### Production Mode (Docker)

Docker runs everything on **port 8000**:
- Frontend: `http://localhost:8000`
- API: `http://localhost:8000/api/*`
- WebSocket: `ws://localhost:8000/ws/*`

## 📝 Environment Variables

Create a `.env` file (or use docker-compose environment section):

```env
PORT=8000
HOST=0.0.0.0
CORS_ORIGINS=http://localhost:8000,https://yourdomain.com
```

## 🗄️ Database Persistence

SQLite database is stored in `./data/fitness.db` and is mounted as a volume, so data persists across container restarts.

## 🔍 How It Works

### Build Process

1. **Frontend Build Stage**:
   - Installs Node.js dependencies
   - Builds SvelteKit app to `build/` directory
   - Creates static HTML/CSS/JS files

2. **Backend Stage**:
   - Installs Python dependencies (MediaPipe, OpenCV, TensorFlow, etc.)
   - Copies backend source code
   - Copies built frontend from Stage 1
   - Sets up to serve both API and frontend

### Runtime

- FastAPI serves:
  - `/api/*` - REST API endpoints
  - `/ws/*` - WebSocket endpoints
  - `/_app/*` - Static assets (JS, CSS, images)
  - `/*` - SPA routes (serves `index.html`)

### WebSocket Connection

Frontend connects to WebSocket using:
```javascript
const wsUrl = `${protocol}//${window.location.hostname}:8000/ws/workout?exercise=${exercise}`;
```

Since frontend and backend are on the same domain in Docker, this works automatically.

## 🐛 Troubleshooting

### Build Fails

```bash
# Check Docker build logs
docker build -t ai-trainer:latest . --no-cache

# Check if all dependencies are in requirements.txt
```

### Container Won't Start

```bash
# Check logs
docker logs ai-trainer

# Check if port 8000 is already in use
lsof -i :8000
```

### Frontend Not Loading

- Check if `build/` directory exists in container:
  ```bash
  docker exec ai-trainer ls -la /app/build
  ```

- Check backend logs for static file serving errors

### Database Issues

- Ensure `data/` directory exists and is writable:
  ```bash
  mkdir -p data
  chmod 755 data
  ```

## 📊 Health Check

Container includes health check:

```bash
# Check container health
docker ps  # Look for "healthy" status

# Manual health check
curl http://localhost:8000/health
```

## 🔄 Updating

### Rebuild After Code Changes

```bash
# Stop container
docker-compose down

# Rebuild
docker-compose build --no-cache

# Start again
docker-compose up -d
```

### Update Dependencies

1. Update `requirements.txt` or `package.json`
2. Rebuild image: `docker-compose build --no-cache`
3. Restart: `docker-compose up -d`

## 🚢 Production Deployment

### DigitalOcean / AWS / Any VPS

1. **Build image on server**:
   ```bash
   git clone <your-repo>
   cd ai_trainer
   docker build -t ai-trainer:latest .
   ```

2. **Run with docker-compose**:
   ```bash
   docker-compose up -d
   ```

3. **Set up reverse proxy (Nginx)**:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }
   }
   ```

4. **Add SSL with Let's Encrypt**:
   ```bash
   certbot --nginx -d yourdomain.com
   ```

## 📦 Image Size

The final image is large (~2-3GB) due to:
- Python ML libraries (TensorFlow, MediaPipe, OpenCV)
- System dependencies for OpenCV

To reduce size, consider:
- Using multi-stage builds more aggressively
- Using Alpine-based images (may need additional dependencies)
- Removing development dependencies

## ✅ Checklist

- [x] Single container (backend + frontend)
- [x] Production build for frontend
- [x] SQLite database persistence
- [x] Environment variables support
- [x] Health checks
- [x] CORS configuration
- [x] WebSocket support
- [x] Static file serving
- [x] SPA routing support

## 🎯 Next Steps

1. Test locally: `docker-compose up`
2. Deploy to your server
3. Set up domain and SSL
4. Configure environment variables
5. Monitor logs: `docker logs -f ai-trainer`


