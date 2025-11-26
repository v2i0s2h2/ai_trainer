# Multi-stage Dockerfile for AI Trainer
# Stage 1: Frontend Build
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY svelte.config.js vite.config.ts tsconfig.json ./
COPY src/frontend ./src/frontend

# Build frontend
RUN npm run build

# Stage 2: Python Backend
FROM python:3.11-slim AS backend

WORKDIR /app

# Install system dependencies for OpenCV and MediaPipe
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY src/backend ./src/backend
COPY startup_backend.py .
COPY scripts/ ./scripts/

# Copy built frontend from previous stage
# SvelteKit builds to 'build' directory
COPY --from=frontend-builder /app/build ./build

# Create data directory for SQLite
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Environment variables (can be overridden)
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV HOST=0.0.0.0

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start command
CMD ["python", "startup_backend.py"]

