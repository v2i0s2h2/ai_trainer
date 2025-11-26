.PHONY: build build-backend build-frontend run stop logs logs-backend logs-frontend restart clean rebuild help

# Docker commands for AI Trainer (Multi-Container)

build:
	@echo "🔨 Building both containers..."
	docker-compose build

build-backend:
	@echo "🔨 Building backend container..."
	docker-compose build backend

build-frontend:
	@echo "🔨 Building frontend container..."
	docker-compose build frontend

run:
	@echo "🚀 Starting containers..."
	docker-compose up -d

stop:
	@echo "🛑 Stopping containers..."
	docker-compose down

logs:
	@echo "📋 Showing all logs..."
	docker-compose logs -f

logs-backend:
	@echo "📋 Showing backend logs..."
	docker-compose logs -f backend

logs-frontend:
	@echo "📋 Showing frontend logs..."
	docker-compose logs -f frontend

restart:
	@echo "🔄 Restarting containers..."
	docker-compose restart

clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	docker rmi ai-trainer-backend ai-trainer-frontend 2>/dev/null || true

rebuild:
	@echo "🔨 Rebuilding and restarting..."
	docker-compose build --no-cache
	docker-compose up -d

help:
	@echo "AI Trainer Docker Commands (Multi-Container):"
	@echo "  make build          - Build both containers"
	@echo "  make build-backend  - Build backend only"
	@echo "  make build-frontend - Build frontend only"
	@echo "  make run            - Start containers (docker-compose up -d)"
	@echo "  make stop           - Stop containers"
	@echo "  make logs           - Show all logs"
	@echo "  make logs-backend   - Show backend logs"
	@echo "  make logs-frontend  - Show frontend logs"
	@echo "  make restart        - Restart containers"
	@echo "  make rebuild        - Rebuild and restart"
	@echo "  make clean          - Remove containers and images"
	@echo "  make help           - Show this help"


