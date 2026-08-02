.PHONY: help setup lock test collect stress api-test benchmark coverage validate lint format typecheck docs ci audit docker-dev docker-prod docker-gpu clean

# ────────────────────────────────────────────────────────────────────────────────
# KuroAI Makefile — Developer Commands & Automation
# ────────────────────────────────────────────────────────────────────────────────

PYTHON     := python
PIP        := pip
PYTEST     := $(PYTHON) -m pytest

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup:  ## Run developer setup & bootstrap script
	$(PYTHON) scripts/bootstrap.py

lock:  ## Regenerate requirements/runtime.lock file
	$(PIP) freeze > requirements/runtime.lock

test:  ## Run full unit test suite
	$(PYTEST) tests/ -q --ignore=tests/stress

collect:  ## Run test collection gate
	$(PYTEST) --collect-only -q

stress:  ## Run stress and concurrency test suite
	$(PYTEST) tests/stress/ -v

api-test:  ## Run public API stability tests
	$(PYTEST) tests/test_public_api.py -v

benchmark:  ## Run benchmark suite and export reports (JSON, CSV, MD)
	$(PYTHON) -m benchmarks.runner

coverage:  ## Calculate layer-by-layer test coverage
	$(PYTHON) -m coverage run -m pytest tests/ --ignore=tests/stress -q
	$(PYTHON) -m coverage report --fail-under=80

validate:  ## Run architecture validator (must return 0 violations)
	$(PYTHON) scripts/architecture_validator.py

lint:  ## Run ruff linter
	$(PYTHON) -m ruff check backend/ config/ scripts/ tests/ benchmarks/

format:  ## Auto-format code with black & isort
	$(PYTHON) -m black backend/ config/ scripts/ tests/ benchmarks/
	$(PYTHON) -m isort backend/ config/ scripts/ tests/ benchmarks/

typecheck:  ## Run mypy type checker
	$(PYTHON) -m mypy backend/ config/ --ignore-missing-imports

docs:  ## Build MkDocs documentation site
	$(PYTHON) -m mkdocs build

ci: validate format lint typecheck collect test coverage  ## Run full CI verification suite locally

audit:  ## Run repository health gate audit
	$(PYTHON) scripts/repo_audit.py

docker-dev:  ## Start development docker-compose stack
	docker-compose -f docker-compose.dev.yml up --build

docker-prod:  ## Start production docker-compose stack
	docker-compose -f docker-compose.prod.yml up -d

docker-gpu:  ## Start GPU inference docker-compose stack
	docker-compose -f docker-compose.gpu.yml up -d

clean:  ## Remove build artifacts, caches, and logs
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .coverage coverage_html site/
