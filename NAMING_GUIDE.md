# KuroAI — Naming Guide

> Frozen as of RC-1. Consistent naming is a stability guarantee. Breaking a naming convention requires an ADR.

---

## 1. Classes

| Pattern | Rule | Example |
|---|---|---|
| Registry classes | `<Resource>Registry` | `ArtifactRegistry`, `AgentRegistry`, `CapabilityRegistry` |
| Engine / stateful | `<Domain>Engine` | `ProjectStateEngine`, `ContextEngine` |
| Graph classes | `<Domain>Graph` | `DependencyGraph`, `VersionGraph` |
| Bus / queue | `<Domain>Bus` | `EventBus` |
| Scheduler | `<Domain>Scheduler` | `TaskScheduler` |
| Runtime | `<Domain>Runtime` | `AgentRuntime` |
| Agents | `<Name>Agent` | `StoryAgent`, `SceneAgent` |
| Providers | `<Name>Provider` | `OpenAIProvider`, `OllamaProvider` |
| Errors | `<Domain>Error` | `AgentRuntimeError`, `ContractValidationError`, `RegistryError` |
| Abstract base | `Base<Name>` | `BaseAgent`, `BaseProvider`, `BaseRetriever` |
| Contracts (data) | Plain noun | `Artifact`, `Task`, `ToolRequest`, `ContextBundle` |

---

## 2. Methods

### Public API Methods (Frozen)

| Verb | Meaning | Example |
|---|---|---|
| `register` | Add something to a registry for the first time | `register_artifact()`, `register_agent()` |
| `update` | Modify an existing entry | `update_status()` |
| `get` | Retrieve by ID (raises if not found) | `get_artifact()`, `get_task()` |
| `exists` | Return bool without raising | `exists(artifact_id)` |
| `list` | Return all items | `list_tasks()`, `list_agents()` |
| `execute` | Run a tool or task | `execute_tool()`, `execute_task()` |
| `schedule` | Queue a task for execution | `schedule(task)` |
| `cancel` | Stop a scheduled or running task | `cancel_task(task_id)` |
| `publish` | Emit an event | `publish(event)` |
| `subscribe` | Register a listener | `subscribe(event_type, handler)` |
| `assemble` | Build a compound object | `assemble_context()` |
| `detect` | Scan for a property | `detect_cycles()` |

### Private Convention

- One leading underscore: `_build_context()`, `_validate_artifact()`
- Double leading underscore only for name mangling (rarely needed)

---

## 3. Variables

| Pattern | Rule |
|---|---|
| `snake_case` | All variable and parameter names |
| `_private_var` | Instance variables not part of public API |
| `UPPER_SNAKE` | Module-level constants only |
| `artifact_id`, `task_id` | Always suffix IDs with `_id` |
| `agent_type` | Discriminator string for polymorphic dispatch |
| `capability_type` | Discriminator string for provider resolution |

---

## 4. Modules / Files

| Pattern | Rule |
|---|---|
| `snake_case.py` | All module files |
| `<resource>_registry.py` | Registry modules (e.g., `agent_registry.py`) |
| `<domain>_engine.py` | Engine modules |
| `<domain>_graph.py` | Graph modules |
| One class per file | Preferred, except for small data classes |

---

## 5. Packages

| Package | Responsibility |
|---|---|
| `backend.contracts` | Immutable data models |
| `backend.engine` | Stateful blackboard subsystems |
| `backend.agents` | Agent runtime and implementations |
| `backend.capabilities` | Tool execution and providers |
| `backend.shared` | Utilities, logging, exceptions |
| `backend.inference` | LLM clients |
| `config` | Application configuration |

---

## 6. Exception Names

All exceptions inherit from `KuroAIError`. Never shadow Python builtins.

| ❌ Avoid | ✅ Use |
|---|---|
| `RuntimeError` | `AgentRuntimeError` |
| `ValidationError` | `ContractValidationError` |
| `ValueError` | `ContractValidationError` (for contract violations) |
| `KeyError` | `RegistryError` (for missing registry entries) |
