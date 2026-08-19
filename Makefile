# AgentBenchX Makefile

.PHONY: help install dev test lint format clean docker-up docker-down logs

help:
	@echo "AgentBenchX Development Commands"
	@echo ""
	@echo "Usage:"
	@echo "  make help          Show this help message"
	@echo "  make install       Install development dependencies"
	@echo "  make dev           Start development environment"
	@echo "  make test          Run tests"
	@echo "  make lint          Run linting"
	@echo "  make format        Format code"
	@echo "  make clean         Clean temporary files"
	@echo "  make docker-up     Start Docker services"
	@echo "  make docker-stop   Stop Docker services"
	@echo "  make logs          View Docker logs"

# Installation
install:
	pip install -e ".[dev]"
	pip install -r backend/requirements/dev.txt

dev:
	@echo "Starting development environment..."
	docker-compose up

test:
	pytest

lint:
	ruff check .
	mypy backend/app/

format:
	black .
	ruff check . --fix

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete
	find . -type f -name "*.swp" -delete
	docker-compose down -v

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

logs:
	docker-compose logs -f

# Database commands
db-migrate:
	alembic upgrade head

db-reset:
	docker-compose down -v
	docker-compose up -d
	alembic upgrade head

# Backend specific
backend-install:
	cd backend && pip install -e .

backend-test:
	cd backend && pytest

backend-lint:
	cd backend && ruff check . && mypy app/

# Future frontend commands (placeholders)
frontend-install:
	@echo "Frontend not yet implemented"

frontend-dev:
	@echo "Frontend not yet implemented"

frontend-test:
	@echo "Frontend not yet implemented"