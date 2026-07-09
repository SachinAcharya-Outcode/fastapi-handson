# User-configurable variables
PYTHON         ?= python3
PORT           ?= 8000
APP_PORT       ?= 8000
DB_PORT        ?= 5432
DOCKER         ?= docker
DOCKER_COMPOSE ?= docker compose

# Project paths
ROOT_DIR    := $(CURDIR)
VENV_DIR    := $(ROOT_DIR)/.venv
BIN         := $(VENV_DIR)/bin

# Commands
PIPE         := $(BIN)/pip
PYTEST       := $(BIN)/pytest
UVICORN      := $(BIN)/uvicorn
RUFF         := $(BIN)/ruff
MYPY         := $(BIN)/mypy
ALEMBIC      := $(BIN)/alembic
DC           := $(DOCKER_COMPOSE)

# Phony targets
.PHONY: help

# ══════════════════════════════════════════════
## Environment & Setup
# ══════════════════════════════════════════════

$(VENV_DIR):
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created at $(VENV_DIR)."

env: $(VENV_DIR) ## Create virtual environment

install: $(VENV_DIR) ## Install all dependencies (dev + project)
	@echo "Installing dependencies..."
	$(PIPE) install -e .
	$(PIPE) install -r requirements/dev.txt

# ══════════════════════════════════════════════
## Development
# ══════════════════════════════════════════════

dev: ## Start the FastAPI dev server with hot-reload
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port $(PORT)

# ══════════════════════════════════════════════
## Testing & Coverage
# ══════════════════════════════════════════════

test: ## Run tests with short traceback
	@echo "Running tests..."
	$(PYTEST) -v --tb=short

coverage: ## Run tests with coverage report (term + HTML)
	@echo "Running tests with coverage..."
	$(PYTEST) --cov=app --cov-report=term-missing --cov-report=html

# ══════════════════════════════════════════════
## Linting & Formatting
# ══════════════════════════════════════════════

lint: ## Run linters (ruff check + mypy)
	@echo "Running linters..."
	$(RUFF) check .
	$(MYPY) .

lint-fix: ## Auto-fix lint issues where possible
	$(RUFF) check --fix .

format: ## Auto-format code (ruff format + import sorting)
	@echo "Running code formatters..."
	$(RUFF) format .
	$(RUFF) check --fix --select I .

# ══════════════════════════════════════════════
## Database Migrations (Alembic)
# ══════════════════════════════════════════════

migrate: alembic-upgrade ## Alias for alembic-upgrade

alembic-upgrade: ## Apply all pending migrations
	$(ALEMBIC) upgrade head

alembic-downgrade: ## Rollback the last migration
	$(ALEMBIC) downgrade -1

alembic-revision: ## Create a new auto-generated migration (msg="description")
	$(ALEMBIC) revision --autogenerate -m "$(msg)"

alembic-history: ## Show migration history
	$(ALEMBIC) history

alembic-current: ## Show current migration version
	$(ALEMBIC) current

alembic-check: ## Check if migrations are up to date
	$(ALEMBIC) check

# ══════════════════════════════════════════════
## Docker
# ══════════════════════════════════════════════

docker-build: ## Build the base Docker image only
	$(DC) build base

docker-dev: ## Run the app in development mode via Docker
	APP_PORT=$(APP_PORT) DB_PORT=$(DB_PORT) $(DC) --profile development up -d
	@echo "App running at http://localhost:$(APP_PORT)"

docker-prod: ## Run the app in production mode via Docker
	APP_PORT=$(APP_PORT) DB_PORT=$(DB_PORT) $(DC) --profile production up -d
	@echo "App running at http://localhost:$(APP_PORT)"

docker-down: ## Stop and remove all Docker containers
	$(DC) down

docker-logs: ## Tail logs from the backend containers
	$(DC) logs -f backend-dev backend-prod

docker-shell: ## Open a shell inside the running backend-dev container
	$(DC) exec backend-dev /bin/sh

docker-migrate: ## Run pending migrations inside the running backend-dev container
	$(DC) exec backend-dev alembic upgrade head

docker-clean: ## Remove all containers, volumes, and images created by compose
	$(DC) down -v --rmi all

# ══════════════════════════════════════════════
## Housekeeping
# ══════════════════════════════════════════════

clean: ## Remove cache and build artifacts
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/ dist/ *.egg-info htmlcov/
	@echo "Cleaned up."

# ══════════════════════════════════════════════
## Help
# ══════════════════════════════════════════════

help: ## Show this help
	@printf "\033[1mUsage:\033[0m\n  make [target]\n\n"
	@awk 'BEGIN {FS = ":.*##"; group=""} \
		/^## /    {group=substr($$0,4); next} \
		/^[a-zA-Z_-]+:.*## / {if (group && group != last) {printf "\n\033[1m%s\033[0m\n", group; last=group}; \
		printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
