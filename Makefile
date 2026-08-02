.PHONY: help install test stress benchmark lint format typecheck validate docker-dev docker-prod clean

# ────────────────────────────────────────────────────────────────────────────────
# KuroAI Makefile — Developer Commands
# ────────────────────────────────────────────────────────────────────────────────

PYTHON     := python
PIP        := pip
PYTEST     := $(PYTHON) -m pytest
VENV       := venv
VENV_BIN   := $(VENV)/Scripts

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install all dependencies into venv
	$(PIP) install -r requirements.txt

test:  ## Run the full unit test suite
	$(PYTEST) tests/ -q --ignore=tests/stress

stress:  ## Run the stress and concurrency test suite
	$(PYTEST) tests/stress/ -v

api-test:  ## Run public API stability tests
	$(PYTEST) tests/test_public_api.py -v

benchmark:  ## Run the performance benchmark suite
	$(PYTHON) -m benchmarks.runner

validate:  ## Run architecture validator (must return 0 violations)
	$(PYTHON) scripts/architecture_validator.py

lint:  ## Run ruff linter
	$(PYTHON) -m ruff check backend/ config/ scripts/ tests/

format:  ## Auto-format code with black
	$(PYTHON) -m black backend/ config/ scripts/ tests/ benchmarks/

typecheck:  ## Run mypy type checker
	$(PYTHON) -m mypy backend/ config/ --ignore-missing-imports

docker-dev:  ## Start development docker-compose stack
	docker-compose -f docker-compose.dev.yml up --build

docker-prod:  ## Start production docker-compose stack
	docker-compose -f docker-compose.prod.yml up -d

docker-down:  ## Stop all docker-compose stacks
	docker-compose -f docker-compose.dev.yml down
	docker-compose -f docker-compose.prod.yml down

clean:  ## Remove build artifacts, caches, and logs
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -f performance_report.md
	rm -rf .pytest_cache
