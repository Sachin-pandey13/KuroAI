# KuroAI Dependency Audit Report

**Generated at**: 2026-08-02 17:26:51 UTC

**Python Runtime**: 3.11.9 on win32

---

## Executive Summary

- **Total Packages Installed**: `96`
- **Root `requirements.txt` Count**: `9`
- **Lockfile `requirements-lock.txt` Count**: `85`
- **Detected ML Packages**: `7`
- **Detected Dev/Tooling Packages**: `2`

## Proposed Categorization for `requirements/` Directory

### 1. `requirements/runtime.txt` (Core Server)
```text
fastapi>=0.135.1
fpdf2>=2.8.7
jsonschema>=4.26.0
openai>=2.28.0
pillow>=12.0.0
pydantic>=2.12.5
pyyaml>=6.0.3
requests>=2.32.5
uvicorn>=0.41.0
```

### 2. `requirements/dev.txt` (Developer Tooling)
```text
-r runtime.txt
pytest
pytest-asyncio
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