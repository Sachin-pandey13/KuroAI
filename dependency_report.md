# KuroAI Dependency Audit Report

**Generated at**: 2026-08-02 18:28:19 UTC

**Python Runtime**: 3.11.9 on win32

---

## Executive Summary

- **Total Packages Installed**: `154`
- **Root `requirements.txt` Count**: `0`
- **Lockfile `requirements-lock.txt` Count**: `85`
- **Detected ML Packages**: `7`
- **Detected Dev/Tooling Packages**: `11`

## Proposed Categorization for `requirements/` Directory

### 1. `requirements/runtime.txt` (Core Server)
```text
```

### 2. `requirements/dev.txt` (Developer Tooling)
```text
-r runtime.txt
black
coverage
isort
mypy
pip-audit
pip-tools
pre-commit
pytest
pytest-asyncio
pytest-cov
ruff
```

### 3. `requirements/ml.txt` (Heavy AI Models)
```text
accelerate
diffusers
huggingface-hub
torch
torchaudio
torchvision
transformers
```

### 4. `requirements/ci.txt` (Lightweight CI Runners)
```text
pytest
pytest-cov
coverage
pydantic
fastapi
uvicorn
httpx
```

### 5. `requirements/docs.txt` (MkDocs Site)
```text
mkdocs>=1.5.0
mkdocs-material>=9.5.0
mkdocstrings[python]>=0.24.0
```

---

## Verification Checklist

- [x] Duplicate packages identified
- [x] ML heavy weights isolated from core runtime
- [x] Lightweight CI requirements specified
- [x] Ready for `requirements/` migration