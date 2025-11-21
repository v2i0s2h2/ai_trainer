.PHONY: build run stop logs clean help

# Docker commands for AI Trainer

build:
	@echo "🔨 Building Docker image..."
	docker build -t ai-trainer:latest .

run:
	@echo "🚀 Starting container..."
	docker-compose up -d

stop:
	@echo "🛑 Stopping container..."
	docker-compose down

logs:
	@echo "📋 Showing logs..."
	docker-compose logs -f

restart:
	@echo "🔄 Restarting container..."
	docker-compose restart

clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	docker rmi ai-trainer:latest 2>/dev/null || true

rebuild:
	@echo "🔨 Rebuilding and restarting..."
	docker-compose build --no-cache
	docker-compose up -d

help:
	@echo "AI Trainer Docker Commands:"
	@echo "  make build    - Build Docker image"
	@echo "  make run      - Start container (docker-compose up -d)"
	@echo "  make stop     - Stop container"
	@echo "  make logs     - Show container logs"
	@echo "  make restart  - Restart container"
	@echo "  make rebuild  - Rebuild and restart"
	@echo "  make clean    - Remove container and image"
	@echo "  make help     - Show this help"


