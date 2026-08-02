# Getting Started with KuroAI

## Prerequisites

- Python 3.10, 3.11, or 3.12
- Git
- Docker (optional for containerized deployment)

---

## 1. Quick Developer Setup (One Command)

Clone the repository and run the developer bootstrap script:

```bash
git clone https://github.com/Sachin-pandey13/KuroAI.git
cd KuroAI
python scripts/bootstrap.py
```

This will automatically:
1. Verify Python version
2. Install developer dependencies (`requirements/dev.txt`)
3. Setup pre-commit git hooks
4. Run the Architecture Validator

---

## 2. Manual Installation

```bash
# Core server runtime only:
pip install -r requirements/runtime.txt

# Full developer suite:
pip install -r requirements/dev.txt

# Heavy ML dependencies (for local generation):
pip install -r requirements/ml.txt
```

---

## 3. Running the Server locally

```bash
uvicorn backend.api.app:app --reload --port 8000
```

Check health endpoints:
- Liveness: `http://localhost:8000/health/liveness`
- Readiness: `http://localhost:8000/health/readiness`
- Metrics: `http://localhost:8000/metrics`
