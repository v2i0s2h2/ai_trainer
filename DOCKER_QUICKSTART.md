# 🐳 Docker Quick Start

## Build & Run

```bash
# Build image
docker build -t ai-trainer:latest .

# Run with docker-compose (recommended)
docker-compose up -d

# Or run directly
docker run -d -p 8000:8000 -v $(pwd)/data:/app/data ai-trainer:latest
```

## Access

- **Frontend + API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

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


