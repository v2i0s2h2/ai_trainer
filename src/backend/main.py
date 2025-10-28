"""
FastAPI Backend for AI Trainer
Provides REST API and WebSocket endpoints for real-time workout tracking
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers (will create these next)
from src.backend.api import routes
from src.backend.api import websocket as ws

# Register routes
app.include_router(routes.router, prefix="/api")
app.include_router(ws.router)

@app.get("/")
async def root():
    """Health check endpoint"""
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

