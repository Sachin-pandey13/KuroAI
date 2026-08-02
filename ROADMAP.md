# KuroAI Roadmap

## Current: v1.0.0-rc2 (Production Hardening)

Status: **In Progress**

---

## v1.0.0 Final — Stable Release

**Target**: Q3 2025

### Goals
- External security audit (penetration testing on prompt injection paths)
- Community beta testing period (2-4 weeks)
- Final documentation review
- PyPI package publication
- Full API reference documentation site (MkDocs)

---

## v1.1 — Multi-Provider Intelligence

**Target**: Q4 2025

### Features
- **Streaming inference**: Real-time token streaming from OpenAI, Anthropic, and Ollama
- **Provider cost optimizer**: Automatic provider selection based on cost/latency tradeoffs
- **Anthropic Claude integration**: First-class Claude 3.x support in `InferenceProvider`
- **Google Gemini integration**: Gemini Pro and Flash via unified `InferenceProvider` adapter

### Architecture Constraint
No changes to the `Contracts`, `Engine`, or `AgentRuntime` public APIs.

---

## v1.2 — Advanced Orchestration

**Target**: Q1 2026

### Features
- **Parallel agent execution**: Fork/join patterns in `TaskScheduler`
- **Agent memory backends**: Long-term memory via vector store (Chroma, Pinecone)
- **Conditional workflows**: DAG-based branching and merge in `DependencyGraph`
- **Tool registry expansion**: Web search, code execution, file I/O tools

---

## v2.0 — Distributed Runtime

**Target**: Q2 2026

### Features
- **Distributed task queue**: Redis or RabbitMQ-backed `TaskScheduler`
- **Agent sandboxing**: Per-agent resource limits and isolation
- **Multi-node deployment**: Kubernetes-native runtime with horizontal scaling
- **OpenTelemetry native**: First-class OTLP export to Jaeger, Grafana Tempo

> **Note**: v2.0 will introduce breaking changes to the `AgentRuntime` public API.
> A migration guide will be published before release.

---

## Completed

| Version | Milestone | Status |
|---------|-----------|--------|
| v0.9.0 | Initial prototype | ✅ Done |
| v1.0.0-rc1 | Architecture stabilization | ✅ Done |
| v1.0.0-rc2 | Production hardening | 🔄 In Progress |
