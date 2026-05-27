# User-configurable variables
PYTHON      ?= python3
PORT        ?= 8000

# Project paths
ROOT_DIR    := $(CURDIR)
VENV_DIR    := $(ROOT_DIR)/.venv
BIN         := $(VENV_DIR)/bin

# Commands
PIP         := $(BIN)/pip
PYTEST      := $(BIN)/pytest
UVICORN     := $(BIN)/uvicorn
RUFF        := $(BIN)/ruff
MYPY        := $(BIN)/mypy

# Phony targets
.PHONY: help install dev lint format test clean env

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
	$(PIP) install -e ".[dev]"

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