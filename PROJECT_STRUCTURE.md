# KuroAI — Project Structure

> Canonical layout for KuroAI v1.0 RC-1. After this release, the structure below is considered **locked**. Any deviation requires a GitHub Discussion and ADR.

---

## Top-Level Layout

```
kuroai-genai-pipeline/
├── backend/            # Core Python source
│   ├── contracts/      # Immutable data models (Pydantic)
│   ├── engine/         # Stateful subsystems (blackboard)
│   ├── agents/         # Agent runtime and implementations
│   ├── capabilities/   # Provider registry and tool execution
│   ├── shared/         # Shared utilities, exceptions, logging
│   └── inference/      # LLM communication layer
├── config/             # Environment, defaults, constants
├── docs/               # Architecture Decision Records (ADR)
├── scripts/            # Developer tooling
├── tests/              # Pytest suite
├── exceptions.py       # Root re-export for exceptions
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## backend/contracts/

> **Layer:** Core (no deps on other backend layers)

Pydantic data models that define the shared vocabulary. Every other layer imports from here. Nothing in contracts imports from engine, agents, or capabilities.

```
backend/contracts/
├── __init__.py          # __all__ frozen
├── artifact.py          # Artifact, ArtifactStatus, ArtifactType
├── task.py              # Task, TaskStatus, TaskPriority
├── agent_result.py      # AgentResult
├── tool_request.py      # ToolRequest
├── tool_response.py     # ToolResponse
└── context.py           # ContextBundle, ContextSelector
```

**Public API (frozen):** `Artifact`, `ArtifactStatus`, `ArtifactType`, `Task`, `TaskStatus`, `TaskPriority`, `AgentResult`, `ToolRequest`, `ToolResponse`, `ContextBundle`, `ContextSelector`

---

## backend/engine/

> **Layer:** Engine / Blackboard (depends on contracts only)

Stateful subsystems. Each class owns exactly one resource.

```
backend/engine/
├── __init__.py              # __all__ frozen
├── artifact_registry.py     # ArtifactRegistry
├── state_engine.py          # ProjectStateEngine
├── dependency_graph.py      # DependencyGraph
├── version_graph.py         # VersionGraph
├── context_engine.py        # ContextEngine
├── task_registry.py         # TaskRegistry
├── scheduler.py             # TaskScheduler
└── event_bus.py             # EventBus
```

**Public APIs (frozen):**

| Class | Stable Methods |
|---|---|
| `ArtifactRegistry` | `register`, `update`, `get`, `exists` |
| `ProjectStateEngine` | `get_status`, `transition`, `get_history` |
| `DependencyGraph` | `add_node`, `add_edge`, `get_dependencies`, `get_dependents`, `detect_cycles` |
| `VersionGraph` | `add_version`, `get_latest_version`, `get_version_history` |
| `ContextEngine` | `assemble_context`, `register_section_provider` |
| `TaskRegistry` | `register_task`, `get_task`, `update_status`, `list_tasks` |
| `TaskScheduler` | `schedule`, `get_plan`, `cancel_task` |
| `EventBus` | `subscribe`, `publish`, `unsubscribe` |

---

## backend/agents/

> **Layer:** Agents (depends on engine + contracts)

Agent orchestration and implementations.

```
backend/agents/
├── __init__.py          # __all__ frozen
├── base_agent.py        # BaseAgent ABC
├── agent_registry.py    # AgentRegistry
├── runtime.py           # AgentRuntime
└── [specific agents]/   # StoryAgent, etc.
```

**Public APIs (frozen):**

| Class | Stable Methods |
|---|---|
| `AgentRuntime` | `run_task`, `execute_task`, `register_agent`, `get_agent` |
| `AgentRegistry` | `register_agent`, `get_agent`, `exists`, `list_agents` |

---

## backend/capabilities/

> **Layer:** Capabilities / Providers (depends on contracts only)

Tool execution layer. Providers implement `BaseProvider`.

```
backend/capabilities/
├── __init__.py          # __all__ frozen
├── registry.py          # CapabilityRegistry
├── base_provider.py     # BaseProvider ABC
├── resolved_provider.py # ResolvedProvider
└── providers/           # LLM, image, audio providers
```

**Public APIs (frozen):**

| Class | Stable Methods |
|---|---|
| `CapabilityRegistry` | `register`, `resolve`, `execute_tool` |

---

## backend/shared/

> **Layer:** Shared Utilities (no deps on any other backend layer)

```
backend/shared/
├── __init__.py          # re-exports exceptions + get_logger
├── exceptions.py        # Full exception hierarchy
├── logging.py           # get_logger() factory
└── utils/
    ├── id_generator.py  # generate_uuid()
    ├── time_utils.py    # utc_now()
    ├── token_counter.py # estimate_tokens()
    ├── text_utils.py    # strip_markdown(), normalize_error()
    └── error_helpers.py # format_exception()
```

---

## config/

> **Layer:** Configuration (no deps on backend)

```
config/
├── __init__.py
├── defaults.py          # Numeric defaults (timeouts, limits)
├── environment.py       # AppSettings (from env vars via pydantic-settings)
└── constants.py         # Immutable platform constants
```

---

## scripts/

```
scripts/
└── architecture_validator.py   # Enforces layering rules via AST import parsing
```

---

## tests/

```
tests/
├── test_public_api.py    # API stability regression suite (RC-1 freeze)
└── ...                   # Per-subsystem unit + integration tests
```
