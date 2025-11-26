# 🐳 Docker Setup Summary

## Two Options Available

### Option 1: Multi-Container (Recommended) ⭐

**Files:**
- `Dockerfile.backend` - Backend container
- `Dockerfile.frontend` - Frontend container (Nginx)
- `docker-compose.yml` - Orchestrates both
- `nginx.conf` - Nginx proxy configuration

**Architecture:**
- Frontend: Nginx serving static files on port 3000
- Backend: FastAPI on port 8000
- Communication: Nginx proxies `/api/*` and `/ws/*` to backend

**Quick Start:**
```bash
docker-compose build
docker-compose up -d
# Access: http://localhost:3000
```

**Benefits:**
- ✅ Better separation of concerns
- ✅ Independent scaling
- ✅ Nginx optimized for static files
- ✅ Production-ready architecture

### Option 2: Single Container (Legacy)

**Files:**
- `Dockerfile` - Combined backend + frontend

**Architecture:**
- Single container: FastAPI serves both API and static files
- Port: 8000

**Quick Start:**
```bash
docker build -t ai-trainer -f Dockerfile .
docker run -d -p 8000:8000 -v $(pwd)/data:/app/data ai-trainer
# Access: http://localhost:8000
```

**Benefits:**
- ✅ Simpler setup
- ✅ Single container to manage

## 📚 Documentation

- **`DOCKER_MULTI_CONTAINER.md`** - Complete multi-container guide
- **`DOCKER_QUICKSTART.md`** - Quick reference
- **`DOCKER_GUIDE.md`** - Original single-container guide

## 🎯 Recommendation

**Use Multi-Container** for production deployments. It's more scalable and follows best practices.

