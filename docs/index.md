# Welcome to KuroAI

**KuroAI** is an enterprise-grade, multi-agent generative AI pipeline and microservices engine designed for autonomous narrative parsing, structured storytelling, and scalable AI generation.

---

## Key Features

- **Layered Architecture**: Strict dependency separation (`Contracts` → `Engine` → `Agents` → `Inference`).
- **Frozen Public APIs**: Immutable API signatures guaranteed across v1.x releases.
- **Observability & Telemetry**: Distributed tracing, Prometheus metrics, structured event auditing.
- **Resilience**: Circuit breakers, retry policies with jitter, recovery manager, dead-letter queues.
- **Security Guardrails**: Prompt safety validation, path traversal prevention, secret redaction.
- **Multi-OS CI/CD**: Matrix testing on Linux (Ubuntu), Windows, and macOS.

---

## Project Status

- **Current Version**: `1.0.0-rc3`
- **Architecture Status**: Frozen (v1.0)
- **Supported Platforms**: Windows, Linux, macOS

---

## Quick Navigation

- [Getting Started Guide](getting-started.md)
- [Developer Guide](developer-guide.md)
- [Deployment & Docker](deployment.md)
- [Testing & Benchmarking](testing-guide.md)
