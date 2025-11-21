"""
FastAPI Backend for AI Trainer
Provides REST API and WebSocket endpoints for real-time workout tracking
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import os
from typing import Optional

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
        "src.backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

