# KuroAI — Public API Reference

> Frozen as of RC-1. These are the only stable entry points into each subsystem. All other methods are **internal implementation details** and may change without notice.

---

## contracts — Data Models

```python
from backend.contracts import (
    Artifact, ArtifactStatus, ArtifactType,
    Task, TaskStatus, TaskPriority,
    AgentResult,
    ToolRequest, ToolResponse,
    ContextBundle, ContextSelector,
)
```

All contracts are **Pydantic models**. They are immutable after construction. Use `.model_copy(update={...})` for mutations.

---

## engine — Blackboard Subsystems

### ArtifactRegistry

```python
from backend.engine import ArtifactRegistry

registry = ArtifactRegistry()

# Register a new artifact (raises RegistryError if duplicate)
registry.register(artifact: Artifact) -> None

# Update an existing artifact (raises RegistryError if not found)
registry.update(artifact: Artifact) -> None

# Retrieve by ID (raises RegistryError if not found)
registry.get(artifact_id: str) -> Artifact

# Check existence without raising
registry.exists(artifact_id: str) -> bool
```

### ProjectStateEngine

```python
from backend.engine import ProjectStateEngine

engine = ProjectStateEngine()

engine.get_status(artifact_id: str) -> ArtifactStatus
engine.transition(artifact_id: str, new_status: ArtifactStatus, reason: str = "") -> None
engine.get_history(artifact_id: str) -> list[dict]
```

### DependencyGraph

```python
from backend.engine import DependencyGraph

graph = DependencyGraph()

graph.add_node(artifact_id: str) -> None
graph.add_edge(from_id: str, to_id: str) -> None
graph.get_dependencies(artifact_id: str) -> list[str]
graph.get_dependents(artifact_id: str) -> list[str]
graph.detect_cycles() -> bool
```

### VersionGraph

```python
from backend.engine import VersionGraph

vg = VersionGraph()

vg.add_version(artifact_id: str, version: int, content_hash: str) -> None
vg.get_latest_version(artifact_id: str) -> int
vg.get_version_history(artifact_id: str) -> list[dict]
```

### ContextEngine

```python
from backend.engine import ContextEngine

ctx = ContextEngine(artifact_registry, dependency_graph, version_graph)

ctx.assemble_context(task: Task) -> ContextBundle
ctx.register_section_provider(selector: ContextSelector, retriever: BaseRetriever) -> None
```

### TaskRegistry

```python
from backend.engine import TaskRegistry

tr = TaskRegistry()

tr.register_task(task: Task) -> None
tr.get_task(task_id: str) -> Task
tr.update_status(task_id: str, status: TaskStatus) -> None
tr.list_tasks() -> list[Task]
```

### TaskScheduler

```python
from backend.engine import TaskScheduler

scheduler = TaskScheduler(task_registry)

scheduler.schedule(task: Task) -> None
scheduler.get_plan() -> list[Task]
scheduler.cancel_task(task_id: str) -> None
```

### EventBus

```python
from backend.engine import EventBus

bus = EventBus()

bus.subscribe(event_type: str, handler: Callable) -> None
bus.publish(event_type: str, payload: dict) -> None
bus.unsubscribe(event_type: str, handler: Callable) -> None
```

---

## agents — Agent Runtime

### AgentRuntime

```python
from backend.agents import AgentRuntime

runtime = AgentRuntime(
    agent_registry, capability_registry, artifact_registry,
    task_registry, context_engine, event_bus, state_engine
)

await runtime.run_task(task: Task) -> AgentResult
await runtime.execute_task(task: Task) -> AgentResult   # alias
runtime.register_agent(agent: BaseAgent) -> None
runtime.get_agent(agent_type: str) -> BaseAgent
```

### AgentRegistry

```python
from backend.agents import AgentRegistry

ar = AgentRegistry()

ar.register_agent(agent: BaseAgent) -> None
ar.get_agent(agent_type: str) -> BaseAgent
ar.exists(agent_type: str) -> bool
ar.list_agents() -> list[str]
```

---

## capabilities — Tool Execution

### CapabilityRegistry

```python
from backend.capabilities import CapabilityRegistry

cap = CapabilityRegistry()

cap.register(provider: BaseProvider) -> None
cap.resolve(request: ToolRequest) -> ResolvedProvider
cap.execute_tool(request: ToolRequest) -> ToolResponse
```

---

## shared — Utilities & Exceptions

```python
from backend.shared import (
    KuroAIError,
    RegistryError,
    AgentRuntimeError,
    ProviderError,
    SchedulerError,
    ContextError,
    AgentError,
    ContractValidationError,
    get_logger,
)

from backend.shared.utils import (
    generate_uuid,
    utc_now,
    estimate_tokens,
    strip_markdown,
    normalize_error,
)
```

---

## config

```python
from config import get_settings, PLATFORM_NAME, PLATFORM_VERSION

settings = get_settings()
print(settings.log_level)
print(PLATFORM_VERSION)
```
