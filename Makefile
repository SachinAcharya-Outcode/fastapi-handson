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
DC           := $(DOCKER_COMPOSE)

# Phony targets
.PHONY: help install dev lint format test clean env
.PHONY: docker-dev docker-prod docker-down docker-logs docker-shell docker-clean docker-build-base

test: ## Run tests using pytest
	@echo "Running tests..."
	$(PYTEST)

help: ## Display this help
	@echo "Usage:"
	@echo "  make [target] [PYTHON=python3] [PORT=8000]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

$(VENV_DIR): ## Create virtual environment if it doesn't exist
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created at $(VENV_DIR)."

env: $(VENV_DIR) ## Create virtual environment

install: $(VENV_DIR) ## Create venv, install dependencies and hooks
	@echo "Installing dependencies..."
	$(PIP) install -e .
	$(PIP) install -r requirements/dev.txt

dev: ## Run development server locally
	@echo "Starting development server..."
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port $(PORT)

lint: ## Run linters (ruff and mypy)
	@echo "Running linters..."
	$(RUFF) check .
	$(MYPY) .

format: ## Run code formatters
	@echo "Running code formatters..."
	$(RUFF) format .
	$(RUFF) check --fix --select I .

clean: ## Remove cache and build artifacts
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/ dist/ *.egg-info
	@echo "Cleaned up."

# Docker targets

docker-build: ## Build the base Docker image only
	$(DC) build base

docker-dev: ## Run the application in development mode via Docker
	APP_PORT=$(APP_PORT) DB_PORT=$(DB_PORT) $(DC) --profile development up -d
	@echo "App running at http://localhost:$(APP_PORT)"

docker-prod: ## Run the application in production mode via Docker
	APP_PORT=$(APP_PORT) DB_PORT=$(DB_PORT) $(DC) --profile production up -d
	@echo "App running at http://localhost:$(APP_PORT)"

docker-down: ## Stop and remove all Docker containers
	$(DC) down

docker-logs: ## Tail logs from the backend container
	$(DC) logs -f backend-dev backend-prod

docker-shell: ## Open a shell inside the running backend-dev container
	$(DC) exec backend-dev /bin/sh

docker-clean: ## Remove all containers, volumes, and images created by compose
	$(DC) down -v --rmi all
