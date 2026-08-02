# ADR-003 — Agent Runtime Design

**Date:** 2026-08-02
**Status:** Accepted
**Authors:** KuroAI Architecture Team

---

## Context

KuroAI needs a single orchestration point that takes a `Task`, routes it to the correct agent, provides it with context, executes it, and records the result. Without a centralized runtime, this logic would be scattered across pipeline scripts, orchestrators, and individual agents.

---

## Decision

`AgentRuntime` is the **single pipeline executor**. It is the only class that should coordinate between the engine layer and the agent layer.

### Design

```python
class AgentRuntime:
    async def run_task(self, task: Task) -> AgentResult
    async def execute_task(self, task: Task) -> AgentResult   # alias
    def register_agent(self, agent: BaseAgent) -> None
    def get_agent(self, agent_type: str) -> BaseAgent
```

### Execution Pipeline

```
run_task(task)
    1. task_registry.update_status(task.task_id, RUNNING)
    2. event_bus.publish("task.started", {...})
    3. context = context_engine.assemble_context(task)
    4. agent = agent_registry.get_agent(task.agent_type)
    5. result = await agent.execute(task, context)
    6. artifact_registry.update(result.artifact) if result.artifact
    7. state_engine.transition(artifact_id, new_status)
    8. task_registry.update_status(task.task_id, COMPLETED)
    9. event_bus.publish("task.completed", {...})
    10. return result
```

### Separation of Concerns

| Concern | Owner |
|---|---|
| Task routing | `AgentRuntime` |
| Agent storage | `AgentRegistry` |
| Context assembly | `ContextEngine` |
| Tool execution | `CapabilityRegistry` |
| State transitions | `ProjectStateEngine` |
| Event notifications | `EventBus` |

`AgentRuntime` coordinates, it does not implement any of the above directly.

---

## Consequences

**Positive:**
- One place to add cross-cutting concerns (logging, metrics, retry, human review).
- Agents are pure: they receive `(task, context)` and return `AgentResult`.
- Pipeline is fully observable via EventBus events.

**Negative:**
- `AgentRuntime` depends on all blackboard subsystems — it is inherently high-coupling.
- This is acceptable because `AgentRuntime` is the orchestration boundary, not a domain class.

**Mitigations:**
- All subsystem dependencies are injected via constructor — no service locator, no globals.
- `AgentRuntime` itself is unit-testable with mocked dependencies.
