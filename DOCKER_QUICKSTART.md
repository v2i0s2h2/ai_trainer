# 🐳 Docker Quick Start

## Multi-Container Setup (Recommended)

### Build & Run

```bash
# Build both containers
docker-compose build

# Start both services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Access

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Single Container Setup (Legacy)

If you prefer single container, use the original `Dockerfile`:

```bash
docker build -t ai-trainer:latest -f Dockerfile .
docker run -d -p 8000:8000 -v $(pwd)/data:/app/data ai-trainer:latest
```

## Commands

```bash
# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart

# Rebuild after code changes
docker-compose build --no-cache
docker-compose up -d
```

## Files Created

- `Dockerfile` - Multi-stage build (frontend + backend)
- `docker-compose.yml` - Container orchestration
- `.dockerignore` - Exclude files from build
- `DOCKER_GUIDE.md` - Full documentation

## How It Works

1. **Build Stage**: Compiles SvelteKit frontend to static files
2. **Runtime**: FastAPI serves both API and frontend on port 8000
3. **Database**: SQLite stored in `./data` (persisted via volume)

## Production Deployment

1. Build on server: `docker build -t ai-trainer:latest .`
2. Run: `docker-compose up -d`
3. Set up Nginx reverse proxy
4. Add SSL with Let's Encrypt

See `DOCKER_GUIDE.md` for detailed instructions.


