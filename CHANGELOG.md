# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0-rc2] - 2025-08-02

### Added — RC-2 Production Hardening

**RC-2.1 — Observability & Telemetry**
- `backend/telemetry/` — Exporter-agnostic tracing (`Span`, `Tracer`, `contextvars`-based propagation)
- `backend/telemetry/metrics.py` — `Counter`, `Gauge`, `Histogram`, `Timer` with thread-safe accumulation
- `backend/telemetry/event_audit.py` — `EventAuditRegistry` for structured event counting
- `backend/telemetry/telemetry_manager.py` — Central registry with Prometheus exposition output
- `backend/api/app.py` — FastAPI health (`/health/liveness`, `/health/readiness`) and metrics (`/metrics`) endpoints

**RC-2.2 — Performance Benchmarks**
- `benchmarks/bench_dependency_graph.py` — DAG construction and traversal benchmarks
- `benchmarks/bench_context_engine.py` — Context window construction benchmarks
- `benchmarks/bench_scheduler.py` — Task scheduler throughput benchmarks
- `benchmarks/runner.py` — Benchmark runner with CPU/memory tracking and `performance_report.md` output

**RC-2.3 — Stress & Concurrency Tests**
- `tests/stress/test_event_bus_stress.py` — 10,000-event throughput test
- `tests/stress/test_graph_scale.py` — 10,000-node DAG scale test
- `tests/stress/test_deterministic_concurrency.py` — Deterministic execution plan hash verification

**RC-2.4 — Security**
- `backend/security/input_validator.py` — `PromptSafetyValidator`, path traversal guards, filename sanitization
- `backend/security/redaction.py` — `SecretRedactor` with regex-based credential masking
- `backend/security/secret_manager.py` — `SecretManager` for environment-variable-based secret resolution
- `backend/security/rate_limit.py` — `TokenBucketRateLimiter`, `SlidingWindowRateLimiter`

**RC-2.5 — Resilience**
- `backend/resilience/circuit_breaker.py` — `CircuitBreaker` (CLOSED/OPEN/HALF_OPEN state machine)
- `backend/resilience/retry_policy.py` — `RetryPolicy` with exponential backoff and jitter
- `backend/resilience/recovery_manager.py` — Checkpoint save/restore, dead-letter queue, poison task detection, graceful shutdown

**RC-2.6 — Deployment**
- `Dockerfile` — Multi-stage build (builder + runtime, non-root user)
- `docker-compose.dev.yml` — Development stack with hot reload
- `docker-compose.prod.yml` — Production stack with multi-worker uvicorn
- `.env.example` — Environment variable template

**RC-2.7 — CI/CD**
- `.github/workflows/ci.yml` — Pull request and push CI (validate → test → coverage)
- `.github/workflows/benchmarks.yml` — Weekly benchmark and stress test workflow
- `.github/workflows/release.yml` — Tag-triggered release automation
- `.pre-commit-config.yaml` — black, ruff, mypy, architecture validator hooks
- `Makefile` — Developer command shortcuts

**RC-2.8 — Release Packaging**
- `RELEASE_NOTES.md` — Detailed release notes for v1.0.0-rc2
- `ROADMAP.md` — Post-RC-2 development roadmap
- `CONTRIBUTING.md` — Contributor guide
- `SECURITY.md` — Security policy and vulnerability reporting process
- `CODE_OF_CONDUCT.md` — Community standards

### Changed
- `backend/engine/event_bus.py` — `publish()` now accepts both `Event` objects and `(event_type, payload)` tuples
- `backend/engine/dependency_graph.py` — `add_edge()` now accepts multi-argument and list-based dependency inputs
- `backend/engine/version_graph.py` — Added `add_version()` as canonical alias for `record_version()`
- `backend/security/input_validator.py` — `sanitize_filename()` now raises `InputValidationError` on path separator characters before basename normalization

---

## [1.0.0-rc1] - 2025-07-20

### Added — RC-1 Architecture Stabilization

**RC-1A — Code Refactoring**
- Unified exception hierarchy: `KuroAIBaseError`, `AgentRuntimeError`, `ContractValidationError`, `InfrastructureError`
- Generic utilities only: `generate_uuid()`, `utc_now()`, `estimate_tokens()`, `strip_markdown()`, `normalize_error()`
- `backend/engine/dependency_graph.py` — `DependencyGraph` with cycle detection
- `backend/engine/context_engine.py` — `ContextEngine.build_context()` with token-aware windowing
- `backend/engine/artifact_registry.py` — `ArtifactRegistry.register()` / `.retrieve()` public API frozen
- `backend/engine/agent_runtime.py` — `AgentRuntime.run_task()` public API frozen
- `backend/engine/task_scheduler.py` — Deterministic priority-based scheduler

**RC-1B — Architecture Documentation**
- `ARCHITECTURE_v1.md` — Frozen architecture specification
- `docs/ADR/` — Architecture Decision Records
- `PUBLIC_API.md` — Frozen public API surface documentation
- `scripts/architecture_validator.py` — Automated architecture layer enforcement

---

## [0.9.0] - 2025-07-01

### Added
- Initial generative AI pipeline prototype
- Multi-agent orchestration framework
- OpenAI and Ollama inference providers
- Basic artifact storage and retrieval
