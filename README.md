<div align="center">
  <img src="https://raw.githubusercontent.com/Sachin-pandey13/KuroAI/main/frontend/public/icons.svg" alt="KuroAI Logo" width="120" />
  <h1>KuroAI : Enterprise Generative AI Pipeline Engine</h1>
  <p><em>An enterprise-grade, multi-agent generative AI storytelling engine and microservices architecture.</em></p>

  <!-- Badges -->
  <p>
    <a href="https://github.com/Sachin-pandey13/KuroAI/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/Sachin-pandey13/KuroAI/ci.yml?branch=main&label=CI&style=for-the-badge&logo=github" alt="CI Status" /></a>
    <a href="https://github.com/Sachin-pandey13/KuroAI/actions/workflows/codeql.yml"><img src="https://img.shields.io/github/actions/workflow/status/Sachin-pandey13/KuroAI/codeql.yml?branch=main&label=CodeQL&style=for-the-badge&logo=github" alt="CodeQL" /></a>
    <img src="https://img.shields.io/badge/Coverage-92%25-brightgreen?style=for-the-badge&logo=pytest" alt="Coverage" />
    <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue?style=for-the-badge&logo=python" alt="Python Versions" />
    <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
    <img src="https://img.shields.io/badge/Release-v1.0.0--rc3-orange?style=for-the-badge" alt="Release" />
  </p>
</div>

---

## 📌 Project Status

| Metric | Status |
|---|---|
| **Current Milestone** | `v1.0.0-rc3` (Developer Experience & CI/CD) |
| **Architecture Status** | Frozen v1.0 (0 layer violations) |
| **Public API Surface** | Frozen & Stable |
| **Next Phase** | Phase 3 (Advanced AI Intelligence) |

---

## 💻 Supported Platforms

- **Linux**: Ubuntu 20.04+ (Fully Tested)
- **Windows**: Windows 10/11 (Fully Tested)
- **macOS**: macOS 12+ (Fully Tested)

---

## 🎯 Overview & Architecture

KuroAI operates on a strict multi-layer architecture designed for deterministic execution, high performance, and total operational resilience.

```
Contracts (Immutable Schemas)
    ↑
Engine (ContextEngine, DependencyGraph, AgentRuntime)
    ↑
Agents & Capabilities (Story, Script, Director, Image)
    ↑
Inference (LLM Adapters & Image Generation Providers)
```

- **Contracts**: Zero-dependency Pydantic models defining pipeline schemas.
- **Engine**: Context assembly, DAG dependency sorting, and task scheduling.
- **Resilience**: Circuit Breaker state machines, exponential backoff retries, dead-letter queues.
- **Security**: Prompt injection validator, secret redactor, token bucket rate limiters.
- **Telemetry**: Exporter-agnostic tracing, Prometheus metrics, structured event logging.

---

## ⚡ Quick Start (Developer Setup)

Set up a complete development environment in **one command**:

```bash
git clone https://github.com/Sachin-pandey13/KuroAI.git
cd KuroAI
python scripts/bootstrap.py
```

This automatically installs dependencies, configures pre-commit hooks, and runs the architecture validator.

### Run Local API Server
```bash
uvicorn backend.api.app:app --reload --port 8000
```
- Liveness Probe: `http://localhost:8000/health/liveness`
- Readiness Probe: `http://localhost:8000/health/readiness`
- Metrics: `http://localhost:8000/metrics`

---

## 🐳 Docker Deployment

KuroAI includes three dedicated Docker Compose stacks:

```bash
# Development (Hot Reloading)
docker-compose -f docker-compose.dev.yml up --build

# Production (Multi-Worker Uvicorn)
docker-compose -f docker-compose.prod.yml up -d

# GPU-Accelerated Local Inference (NVIDIA CUDA)
docker-compose -f docker-compose.gpu.yml up -d
```

---

## 📚 Documentation Site

Full documentation is built with MkDocs Material:

```bash
pip install -r requirements/docs.txt
mkdocs serve
```

Browse docs at `http://localhost:8000`:
- [Getting Started Guide](docs/getting-started.md)
- [Developer Guide](docs/developer-guide.md)
- [Versioning Policy](docs/versioning.md)
- [Architecture v1 Specification](ARCHITECTURE_v1.md)
- [Testing & Benchmarks](docs/testing-guide.md)

---

## 🧪 Testing & Audit

```bash
# Run unit tests
make test

# Run stress & concurrency tests
make stress

# Run benchmark suite (exports JSON, CSV, MD)
make benchmark

# Calculate layer coverage
make coverage

# Run 16-Point Repository Quality Audit
make audit
```

---

## 📄 License & Citation

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.

If using KuroAI in research or open-source software, please see [CITATION.cff](CITATION.cff).

---
<div align="center">
  Built by <b>Sachin Pandey</b> & KuroAI Open Source Contributors
</div>
