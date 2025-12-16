"""
FastAPI Backend for AI Trainer
Provides REST API and WebSocket endpoints for real-time workout tracking
"""

import logging
import os
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

AGENT_ENV: str = os.getenv("DEPLOYMENT_ENV", "development")
DEV_MODE: bool = AGENT_ENV == "development"


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Trainer API",
    description="Real-time pose detection and workout tracking API",
    version="1.0.0",
)

# CORS middleware for frontend communication
# Explicitly list allowed origins - wildcard doesn't work with credentials
default_origins = [
    "http://localhost:5173",
    "http://localhost:8001",
    "http://localhost:8000",
]
# Allow additional origins from environment variable
env_origins = (
    os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []
)
cors_origins = (
    default_origins + [o.strip() for o in env_origins if o.strip()]
    if DEV_MODE
    else [o.strip() for o in env_origins if o.strip()]
)

# Allow all Cloudflare Pages deployment URLs (each has unique subdomain like 00cd92a2.ai-trainer-em7.pages.dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"https://[a-z0-9]+\.ai-trainer-em7\.pages\.dev",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
try:
    from src.backend.api import auth, routes
    from src.backend.api import websocket as ws
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path

    root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(root))
    from src.backend.api import auth, routes
    from src.backend.api import websocket as ws

# Register routes
app.include_router(auth.router, prefix="/api")
app.include_router(routes.router, prefix="/api")
app.include_router(ws.router)


@app.get("/")
async def root():
    """API root endpoint"""
    return {"status": "ok", "message": "AI Trainer API is running"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    logger.info("Starting AI Trainer Backend on http://localhost:8000")
    uvicorn.run(
        "src.backend.main:app", host="0.0.0.0", port=8001, reload=True, log_level="info"
    )
