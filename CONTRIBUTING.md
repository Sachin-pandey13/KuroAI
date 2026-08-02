# Contributing to KuroAI

Thank you for your interest in contributing! This guide explains the process and standards.

---

## Quick Start

```bash
# 1. Fork and clone the repository
git clone https://github.com/<your-username>/KuroAI.git
cd KuroAI

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install pre-commit hooks
pip install pre-commit
pre-commit install

# 5. Run the full test suite to confirm your environment is working
python -m pytest tests/ -q
```

---

## Architecture Rules (Non-Negotiable)

KuroAI enforces strict architectural boundaries. These are automatically checked by `scripts/architecture_validator.py` and the pre-commit hook.

```
Contracts  ←  Engine  ←  Agents / Capabilities  ←  Inference
```

| Layer | May Import From | May NOT Import From |
|-------|----------------|---------------------|
| `contracts/` | stdlib only | `engine/`, `agents/`, `inference/` |
| `engine/` | `contracts/`, stdlib | `agents/`, `inference/` |
| `agents/` | `engine/`, `contracts/` | `inference/` directly |
| `inference/` | `contracts/` | `engine/`, `agents/` |

**If your PR introduces a violation, CI will fail and the PR will not be merged.**

---

## Public API Freeze

The following APIs are frozen as of v1.0.0-rc1 and **must not change signature**:

- `ArtifactRegistry.register()` / `.retrieve()`
- `ContextEngine.build_context()`
- `AgentRuntime.run_task()`

Additions are allowed. Removals or signature changes require a new major version.

---

## Contribution Workflow

1. **Open an issue first** for non-trivial changes (features, refactors)
2. **Branch naming**: `feature/short-description`, `fix/short-description`, `docs/short-description`
3. **Commits**: Use conventional commit format: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
4. **Tests required**: Every functional change must include corresponding tests
5. **Architecture Validator must pass**: Run `python scripts/architecture_validator.py` locally
6. **PR description**: Fill out the template completely

---

## Code Standards

| Tool | Purpose | Config |
|------|---------|--------|
| `black` | Formatting | `pyproject.toml` |
| `ruff` | Linting | `pyproject.toml` |
| `mypy` | Type checking | `mypy.ini` |
| `pytest` | Testing | `pytest.ini` |

All are enforced by pre-commit hooks. Run manually:

```bash
python -m black backend/ tests/
python -m ruff check backend/ tests/ --fix
python -m mypy backend/ --ignore-missing-imports
```

---

## Security Issues

**Do not open a public GitHub issue for security vulnerabilities.**

See [SECURITY.md](SECURITY.md) for the responsible disclosure process.

---

## Code of Conduct

All contributors must follow our [Code of Conduct](CODE_OF_CONDUCT.md).
