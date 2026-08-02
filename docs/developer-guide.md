# Developer Guide

## Repository Structure

```
KuroAI/
├── backend/
│   ├── contracts/     # Immutable schemas and Pydantic models
│   ├── engine/        # ContextEngine, DependencyGraph, AgentRuntime
│   ├── agents/        # Story, Script, Director, Image agents
│   ├── inference/     # LLM and Image generation provider adapters
│   ├── resilience/    # CircuitBreaker, RetryPolicy, RecoveryManager
│   ├── security/      # PromptSafetyValidator, SecretRedactor, RateLimiter
│   └── telemetry/     # Tracer, Span, Metrics, EventAuditRegistry
├── requirements/      # Clean requirements (runtime, dev, ci, ml, docs, lock)
├── scripts/           # Architecture validator, dependency audit, repo audit, bootstrap
├── tests/             # Unit, integration, security, resilience, stress suites
└── benchmarks/        # Performance benchmark runner and history
```

---

## Developer Commands (`Makefile`)

```bash
make setup      # Run developer bootstrap script
make test       # Run unit test suite
make stress     # Run stress and concurrency tests
make benchmark  # Run performance benchmarks and export reports
make coverage   # Calculate layer coverage
make validate   # Check architecture layer laws
make format     # Auto-format with Black and isort
make lint       # Check linting with Ruff
make typecheck  # Run MyPy type checker
make ci         # Run local CI verification suite
make audit      # Run 16-point repository quality audit
```
