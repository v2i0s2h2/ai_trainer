"""
FastAPI Backend for AI Trainer
Provides REST API and WebSocket endpoints for real-time workout tracking
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
import os
from typing import Optional
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Trainer API",
    description="Real-time pose detection and workout tracking API",
    version="1.0.0"
)

# CORS middleware for frontend communication
# Allow all origins in production, or use CORS_ORIGINS env var
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",") if os.getenv("CORS_ORIGINS") else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
try:
    from src.backend.api import routes
    from src.backend.api import websocket as ws
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(root))
    from src.backend.api import routes
    from src.backend.api import websocket as ws

# Register routes
app.include_router(routes.router, prefix="/api")
app.include_router(ws.router)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

# Serve static files (built frontend) in production
# SvelteKit builds to 'build' directory by default
static_dir = Path(__file__).parent.parent.parent / "build"
if static_dir.exists():
    # Mount static assets (_app contains JS/CSS bundles)
    if (static_dir / "_app").exists():
        app.mount("/_app", StaticFiles(directory=str(static_dir / "_app")), name="static")
    
    # Serve index.html for root and all non-API routes (SPA routing)
    # This must be defined AFTER API routes so API routes take precedence
    @app.get("/")
    async def serve_root():
        """Serve SvelteKit app root"""
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        else:
            return {"status": "ok", "message": "AI Trainer API is running"}
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve SvelteKit app for all non-API routes"""
        # Don't serve API routes, WebSocket, or static assets
        if full_path.startswith("api/") or full_path.startswith("ws/") or full_path.startswith("_app/"):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Serve index.html for SPA routing
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        else:
            raise HTTPException(status_code=404, detail="Frontend not built")
else:
    # Development mode - no static files
    @app.get("/")
    async def root():
        """Health check endpoint"""
        return {"status": "ok", "message": "AI Trainer API is running"}

if __name__ == "__main__":
    logger.info("Starting AI Trainer Backend on http://localhost:8000")
    uvicorn.run(
        "src.backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

