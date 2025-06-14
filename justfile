# Justfile for G検定対策ツール development tasks
# Install just: https://github.com/casey/just

set shell := ["bash", "-uc"]

# Default recipe - show available commands
default:
    @just --list

# Setup development environment
setup:
    @echo "🚀 Setting up development environment..."
    ./scripts/setup.sh

# Backend development commands

# Install backend dependencies
backend-deps:
    cd backend && uv sync --all-extras

# Run backend development server
backend-dev:
    cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run backend tests
backend-test:
    cd backend && uv run pytest tests/ -v

# Backend code quality checks
backend-lint:
    cd backend && uv run ruff check app/

# Backend code formatting
backend-format:
    cd backend && uv run ruff format app/

# Fix backend code issues automatically
backend-fix:
    cd backend && uv run ruff check app/ --fix && uv run ruff format app/

# Backend type checking
backend-typecheck:
    cd backend && uv run mypy app/

# Full backend quality check
backend-quality: backend-lint backend-typecheck
    @echo "✅ Backend quality check completed"

# Frontend development commands

# Install frontend dependencies
frontend-deps:
    cd frontend && npm install

# Run frontend development server
frontend-dev:
    cd frontend && npm run dev

# Run frontend tests
frontend-test:
    cd frontend && npm test

# Frontend linting
frontend-lint:
    cd frontend && npm run lint

# Frontend type checking
frontend-typecheck:
    cd frontend && npm run type-check

# Build frontend for production
frontend-build:
    cd frontend && npm run build

# Full frontend quality check
frontend-quality: frontend-lint frontend-typecheck
    @echo "✅ Frontend quality check completed"

# Docker commands

# Build all Docker images
docker-build:
    docker compose build

# Start all services with Docker
docker-up:
    docker compose up --build

# Stop all Docker services
docker-down:
    docker compose down

# View Docker logs
docker-logs:
    docker compose logs -f

# Database commands

# Run database migrations
db-migrate:
    cd backend && uv run alembic upgrade head

# Create new database migration
db-migration MESSAGE:
    cd backend && uv run alembic revision --autogenerate -m "{{MESSAGE}}"

# Database shell
db-shell:
    sqlite3 data/problems.db

# Testing commands

# Run all tests
test-all: backend-test frontend-test
    @echo "✅ All tests completed"

# Run tests with coverage
test-coverage:
    cd backend && uv run pytest tests/ --cov=app --cov-report=html
    @echo "📊 Coverage report generated in backend/htmlcov/"

# Code quality commands

# Run all quality checks
quality: backend-quality frontend-quality
    @echo "✅ All quality checks completed"

# Fix all auto-fixable issues
fix: backend-fix
    cd frontend && npm run lint:fix
    @echo "🔧 Auto-fixes applied"

# Utility commands

# Clean up generated files
clean:
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    rm -rf backend/htmlcov/ 2>/dev/null || true
    @echo "🧹 Cleanup completed"

# Download ML models
models:
    ./scripts/download_models.sh

# Initialize embeddings
embeddings:
    cd backend && uv run python app/scripts/init_embeddings.py --reset

# Pre-commit setup
pre-commit-install:
    cd backend && uv run pre-commit install

# Run pre-commit on all files
pre-commit-all:
    cd backend && uv run pre-commit run --all-files

# Development workflow

# Quick development setup (run once)
dev-setup: setup backend-deps frontend-deps pre-commit-install
    @echo "🎉 Development environment ready!"

# Quick start for development
dev: backend-dev frontend-dev

# Full CI-like check before commit
ci-check: quality test-all
    @echo "🚀 Ready for commit!"

# Release preparation
release-check: ci-check docker-build
    @echo "📦 Release preparation completed"