.PHONY: dev dev-backend dev-frontend test test-backend test-frontend lint format build clean setup

# Development
dev:
	@echo "Starting development servers..."
	@make dev-backend &
	@make dev-frontend

dev-backend:
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

# Testing
test: test-backend test-frontend

test-backend:
	cd backend && uv run pytest tests/ -v --cov=app --cov-report=term-missing

test-frontend:
	cd frontend && npx vitest run

# Linting
lint:
	cd backend && uv run ruff check app/ tests/
	cd frontend && npx eslint src/ --ext .vue,.ts,.tsx

# Formatting
format:
	cd backend && uv run ruff format app/ tests/
	cd frontend && npx prettier --write src/

# Build
build:
	cd frontend && npm run build
	@echo "Frontend built. Copy dist/ to backend/app/static/ for production."

# Setup
setup:
	cd backend && uv sync
	cd frontend && npm install

# Clean
clean:
	rm -rf backend/.venv backend/__pycache__ backend/.pytest_cache backend/.ruff_cache
	rm -rf frontend/node_modules frontend/dist
	rm -rf docs/site
