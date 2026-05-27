# FastAPI Practice Project

A well-organized FastAPI project structure following best practices.

## Features

- **FastAPI**: Modern, fast (high-performance), web framework for building APIs with Python 3.10+.
- **Pydantic Settings**: Environment-based configuration management.
- **Ruff**: Extremely fast Python linter and code formatter with strict rules (FAST, S, Q, ANN, TCH, etc.).
- **Mypy**: Strict static type checking with Pydantic plugin.
- **API Versioning**: Scalable structure with `/api/v1` prefix.
- **Custom Exceptions**: Centralized error handling in `app/exceptions`.
- **Makefile**: Convenient commands for installation, linting, and running the app.
- **FAST Rules**: Follows FastAPI best practices (Async, Type hints, structured layout).

## Project Structure

```text
.
├── app/
│   ├── api/             # API route handlers
│   │   ├── v1/          # Version 1 of the API
│   │   │   ├── api.py   # Router aggregator
│   │   │   └── endpoints/
│   │   └── deps/        # Modular dependencies
│   ├── core/            # Core configuration (settings, security, etc.)
│   ├── exceptions/      # Custom exceptions and global handlers
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic / Service layer
│   └── main.py          # FastAPI application entry point
├── tests/               # Pytest tests
├── Makefile             # Development task automation
├── pyproject.toml       # Project metadata and tool configuration
└── README.md            # Documentation
```

## Setup & Running

You can set up and run the project using the provided `Makefile` or manually.

### Option 1: Using Makefile (Recommended)

1. **Environment Setup**:
   ```bash
   make env
   ```

2. **Install dependencies**:
   ```bash
   make install
   ```

3. **Run the application**:
   ```bash
   make dev
   ```

### Option 2: Manual Setup

1. **Create Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -e ".[dev]"
   ```

3. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

## Development Commands

If using the `Makefile`:

- **Linting**: `make lint` (Runs Ruff and Mypy)
- **Formatting**: `make format`
- **Testing**: `make test`
- **Clean**: `make clean`

Manual commands:

- **Check Linting**: `ruff check .`
- **Fix**: `ruff check --fix .`
- **Format Code**: `ruff format .`
- **Type Check**: `mypy .`
- **Testing**: `pytest`

## Testing

Run tests with `pytest`:

```bash
pytest
```
