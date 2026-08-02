# KuroAI — Dependency Graph

> Frozen as of RC-1. Imports that violate this graph are caught by `scripts/architecture_validator.py`.

---

## Layer Hierarchy

```
┌──────────────────────────────────────────────┐
│                  config/                     │  ← Application configuration
└─────────────────────┬────────────────────────┘
                      │ (read by)
┌──────────────────────▼────────────────────────┐
│            backend.contracts                  │  ← Core: Pydantic data models
│  (Artifact, Task, AgentResult, ToolRequest…)  │
└──┬──────────────────┬──────────────────┬──────┘
   │                  │                  │
   ▼                  ▼                  ▼
┌──────────┐  ┌───────────────┐  ┌─────────────┐
│ backend  │  │ backend.engine│  │  backend.   │
│ .shared  │  │ (blackboard)  │  │capabilities │
│(utils,   │  │               │  │ (providers) │
│ logging, │  │ ArtifactReg   │  │             │
│ except.) │  │ StateEngine   │  │CapabilityReg│
└──────────┘  │ DependGraph   │  │ BaseProvider│
              │ VersionGraph  │  └──────┬──────┘
              │ ContextEngine │         │
              │ TaskRegistry  │         │
              │ TaskScheduler │         │
              │ EventBus      │         │
              └───────┬───────┘         │
                      │                 │
                      ▼                 │
              ┌───────────────┐         │
              │ backend.agents│◄────────┘
              │               │
              │ AgentRuntime  │
              │ AgentRegistry │
              │ BaseAgent     │
              │ [agents...]   │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ backend.      │
              │ inference     │
              │ (LLM clients) │
              └───────────────┘
```

---

## Allowed Import Directions

| From | May Import | May NOT Import |
|---|---|---|
| `config` | stdlib only | `backend.*` |
| `backend.contracts` | `config`, stdlib | `backend.engine`, `backend.agents`, `backend.capabilities` |
| `backend.shared` | `config`, stdlib | `backend.contracts`, `backend.engine`, `backend.agents` |
| `backend.capabilities` | `backend.contracts`, `backend.shared`, `config` | `backend.engine`, `backend.agents` |
| `backend.engine` | `backend.contracts`, `backend.shared`, `config` | `backend.agents`, `backend.capabilities` |
| `backend.agents` | `backend.contracts`, `backend.engine`, `backend.capabilities`, `backend.shared` | `backend.inference` directly |
| `backend.inference` | `backend.contracts`, `config`, stdlib | `backend.engine`, `backend.agents` |

---

## Enforcement

Run `scripts/architecture_validator.py` to detect violations:

```bash
python scripts/architecture_validator.py
```

Expected output:

```
[SUCCESS] Architecture Validation Passed! 0 violations found.
```

This is run as part of the CI pipeline.
