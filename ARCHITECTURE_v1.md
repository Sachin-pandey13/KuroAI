# KuroAI — Architecture v1.0

> **Status: LOCKED — RC-1**
>
> This document represents the frozen architecture for KuroAI v1.0 Release Candidate 1.
> Changes to this architecture require a GitHub Discussion and a new ADR in `docs/adr/`.

---

## Overview

KuroAI is a generative AI pipeline for creating long-form narrative content (stories, scripts, screenplays) by coordinating specialized AI agents over a shared blackboard.

```
User Idea
    ↓
TaskScheduler (queue)
    ↓
AgentRuntime (orchestrator)
    ↓
ContextEngine (assemble context)
    ↓
Agent (STORY / SCENE / IMAGE / etc.)
    ↓
CapabilityRegistry → Provider (LLM / Image / Audio)
    ↓
ArtifactRegistry (store result)
    ↓
EventBus (notify observers)
```

---

## Core Principles (Locked)

1. **One Responsibility Per Class.** No class mixes concerns.
2. **Strict Layer Direction.** Lower layers never import upper layers.
3. **Contracts First.** All inter-layer communication uses Pydantic models.
4. **EventBus for Cross-Cutting Communication.** Subsystems do not call each other directly.
5. **Public APIs are Small.** Each class exposes ≤8 stable public methods.
6. **No Globals.** All dependencies are injected via constructors.

---

## Subsystem Map

| Subsystem | Class | Layer | Responsibility |
|---|---|---|---|
| Data Models | `Artifact`, `Task`, `AgentResult`, … | Contracts | Shared vocabulary |
| Artifact Store | `ArtifactRegistry` | Engine | CRUD on artifacts |
| State Machine | `ProjectStateEngine` | Engine | Artifact lifecycle transitions |
| DAG | `DependencyGraph` | Engine | Artifact dependency tracking |
| Versioning | `VersionGraph` | Engine | Artifact version history |
| Context | `ContextEngine` | Engine | Pre-agent context assembly |
| Task Queue | `TaskRegistry` + `TaskScheduler` | Engine | Task storage and ordering |
| Events | `EventBus` | Engine | Decoupled cross-subsystem notifications |
| Orchestration | `AgentRuntime` | Agents | Pipeline execution |
| Agent Storage | `AgentRegistry` | Agents | Agent type → instance lookup |
| Tool Execution | `CapabilityRegistry` | Capabilities | Provider resolution and execution |
| LLM Client | `backend.inference` | Inference | OpenAI / Ollama / HF API calls |
| Logging | `get_logger()` | Shared | Structured JSON logging |
| Exceptions | `KuroAIError` hierarchy | Shared | Typed error taxonomy |
| Config | `AppSettings` | Config | Environment-driven config |

---

## Exception Hierarchy

```
KuroAIError
├── RegistryError
│   ├── ArtifactNotFoundError
│   ├── ArtifactAlreadyExistsError
│   ├── TaskNotFoundError
│   └── ProviderNotFoundError
├── AgentRuntimeError
├── ProviderError
├── SchedulerError
├── ContextError
├── AgentError
└── ContractValidationError
```

No class raises `RuntimeError`, `ValueError`, or `KeyError` for domain-level errors.

---

## Public API Summary

All public APIs are frozen. See [PUBLIC_API.md](./PUBLIC_API.md) for full method signatures.

| Class | # Public Methods |
|---|---|
| `ArtifactRegistry` | 4 |
| `ProjectStateEngine` | 3 |
| `DependencyGraph` | 5 |
| `VersionGraph` | 3 |
| `ContextEngine` | 2 |
| `TaskRegistry` | 4 |
| `TaskScheduler` | 3 |
| `EventBus` | 3 |
| `AgentRuntime` | 4 |
| `AgentRegistry` | 4 |
| `CapabilityRegistry` | 3 |

**Total: 38 stable entry points across 11 classes.**

---

## Architecture Invariants (Enforced by `scripts/architecture_validator.py`)

1. `backend.contracts` imports nothing from `backend.*`
2. `backend.engine` does not import from `backend.agents` or `backend.capabilities`
3. `backend.capabilities` does not import from `backend.engine` or `backend.agents`
4. `backend.shared` does not import from `backend.contracts`, `backend.engine`, `backend.agents`
5. `config` does not import from `backend.*`

Run `python scripts/architecture_validator.py` to verify at any time.

---

## What RC-1 Did NOT Change

- No new agents
- No new capabilities or providers
- No new pipeline stages
- No performance optimizations
- No external API endpoints
- No UI changes
- No database changes

RC-1 is a pure architecture stabilization milestone.

---

## Related Documents

| Document | Purpose |
|---|---|
| [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) | Directory layout reference |
| [DEPENDENCY_GRAPH.md](./DEPENDENCY_GRAPH.md) | Import layer rules |
| [NAMING_GUIDE.md](./NAMING_GUIDE.md) | Class, method, variable conventions |
| [PUBLIC_API.md](./PUBLIC_API.md) | Frozen method signatures |
| [docs/adr/ADR-001-event-bus.md](./docs/adr/ADR-001-event-bus.md) | Why EventBus? |
| [docs/adr/ADR-002-context-engine.md](./docs/adr/ADR-002-context-engine.md) | Why ContextEngine? |
| [docs/adr/ADR-003-runtime.md](./docs/adr/ADR-003-runtime.md) | AgentRuntime pipeline |
| [docs/adr/ADR-004-human-review.md](./docs/adr/ADR-004-human-review.md) | Human review gate (RC-2) |
