# 🐳 Multi-Container Docker Setup

## 📦 Architecture

```
┌─────────────────────────────────────────────┐
│         Docker Network                      │
│                                             │
│  ┌──────────────────┐  ┌─────────────────┐│
│  │  Frontend        │  │  Backend         ││
│  │  (Nginx)         │  │  (FastAPI)      ││
│  │  Port: 3000      │  │  Port: 8000      ││
│  │                  │  │                  ││
│  │  - Serves SPA    │  │  - REST API      ││
│  │  - Proxies /api  │  │  - WebSocket     ││
│  │  - Proxies /ws   │  │  - Health check  ││
│  └──────────────────┘  └─────────────────┘│
│         │                      │            │
│         └──────────────────────┘            │
│              Internal Network               │
└─────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Build and Run

```bash
# Build both containers
docker-compose build

# Start both services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Access

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📁 Files Structure

```
├── Dockerfile.backend      # Backend container (Python/FastAPI)
├── Dockerfile.frontend     # Frontend container (Nginx + SvelteKit)
├── docker-compose.yml      # Multi-container orchestration
├── nginx.conf             # Nginx config for frontend
└── .dockerignore          # Files to exclude from build
```

## 🔧 How It Works

### Frontend Container

1. **Build Stage**: Compiles SvelteKit to static files
2. **Runtime**: Nginx serves static files on port 80
3. **Proxy**: Forwards `/api/*` and `/ws/*` to backend container

### Backend Container

1. **Runtime**: FastAPI serves REST API and WebSocket
2. **Port**: 8000 (internal, not exposed directly)
3. **Database**: SQLite in `./data` (volume mounted)

### Communication

- Frontend → Backend: Via Docker network (`http://backend:8000`)
- User → Frontend: `http://localhost:3000`
- User → Backend (direct): `http://localhost:8000` (optional)

## 🔄 Development vs Production

### Development

Use `./scripts/dev.sh` for hot-reload:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

### Production (Docker)

Use `docker-compose`:
- Frontend: `http://localhost:3000` (proxies to backend)
- Backend: `http://localhost:8000` (direct access)

## 📝 Environment Variables

Create `.env` file:

```env
# Backend port (internal)
BACKEND_PORT=8000

# Frontend port (external)
FRONTEND_PORT=3000

# CORS origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## 🛠️ Commands

### Build

```bash
# Build both
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend

# Rebuild without cache
docker-compose build --no-cache
```

### Run

```bash
# Start in background
docker-compose up -d

# Start with logs
docker-compose up

# Start specific service
docker-compose up backend
docker-compose up frontend
```

### Management

```bash
# View logs
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop
docker-compose stop

# Stop and remove
docker-compose down

# Restart
docker-compose restart

# Scale (if needed)
docker-compose up -d --scale backend=2
```

## 🔍 Troubleshooting

### Frontend can't connect to backend

1. Check if backend is running:
   ```bash
   docker-compose ps
   ```

2. Check backend logs:
   ```bash
   docker-compose logs backend
   ```

3. Test backend directly:
   ```bash
   curl http://localhost:8000/health
   ```

4. Check nginx config:
   ```bash
   docker exec ai-trainer-frontend nginx -t
   ```

### Port conflicts

If ports are already in use:

```bash
# Change ports in docker-compose.yml or .env
FRONTEND_PORT=3001
BACKEND_PORT=8001
```

### Database issues

Ensure `data/` directory exists and is writable:

```bash
mkdir -p data
chmod 755 data
```

## 🚢 Production Deployment

### 1. Build on Server

```bash
git clone <your-repo>
cd ai_trainer
docker-compose build
```

### 2. Run

```bash
docker-compose up -d
```

### 3. Set up Reverse Proxy (Optional)

If you want a single domain:

```nginx
# /etc/nginx/sites-available/ai-trainer
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. SSL with Let's Encrypt

```bash
certbot --nginx -d yourdomain.com
```

## 📊 Benefits of Multi-Container

✅ **Separation of Concerns**: Frontend and backend are independent
✅ **Independent Scaling**: Scale frontend/backend separately
✅ **Better Caching**: Nginx handles static files efficiently
✅ **Easier Updates**: Update frontend without rebuilding backend
✅ **Production Ready**: Nginx is optimized for serving static files
✅ **Network Isolation**: Containers communicate via Docker network

## 🔄 Updating

### Update Frontend Only

```bash
docker-compose build frontend
docker-compose up -d frontend
```

### Update Backend Only

```bash
docker-compose build backend
docker-compose up -d backend
```

### Update Both

```bash
docker-compose build
docker-compose up -d
```

## 📦 Container Details

### Backend Container

- **Base Image**: `python:3.11-slim`
- **Size**: ~2-3GB (ML libraries)
- **Port**: 8000 (internal)
- **Volumes**: `./data`, `./models`

### Frontend Container

- **Base Image**: `nginx:alpine`
- **Size**: ~50MB (very small!)
- **Port**: 80 (mapped to 3000)
- **Volumes**: None (static files baked in)

## 🎯 Comparison: Single vs Multi-Container

| Feature | Single Container | Multi-Container |
|---------|-----------------|-----------------|
| Simplicity | ✅ Simpler | ❌ More complex |
| Size | Large (all in one) | Smaller (separate) |
| Scaling | ❌ Scale together | ✅ Scale independently |
| Updates | Rebuild all | Update separately |
| Static Files | FastAPI serves | Nginx serves (faster) |
| Production | Works | ✅ Better optimized |

## ✅ Checklist

- [x] Separate backend container
- [x] Separate frontend container
- [x] Nginx proxy configuration
- [x] Docker network setup
- [x] Health checks for both
- [x] Volume mounts for database
- [x] Environment variables
- [x] CORS configuration
- [x] WebSocket proxy support

## 🎉 Next Steps

1. Test locally: `docker-compose up`
2. Verify both containers: `docker-compose ps`
3. Check logs: `docker-compose logs -f`
4. Deploy to production
5. Set up monitoring

