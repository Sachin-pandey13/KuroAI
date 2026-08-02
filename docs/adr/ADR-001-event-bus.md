# ADR-001 — Event Bus Architecture

**Date:** 2026-08-02
**Status:** Accepted
**Authors:** KuroAI Architecture Team

---

## Context

KuroAI's subsystems need to communicate state changes without creating tight coupling. For example:

- When `ArtifactRegistry` registers an artifact, `ProjectStateEngine` should initialize status.
- When `AgentRuntime` completes a task, `TaskRegistry` should update task status.
- When `ProjectStateEngine` transitions state, downstream observers may need to react.

The naive approach — direct method calls between subsystems — creates a dense dependency web that contradicts the single-responsibility principle and makes the system hard to test in isolation.

---

## Decision

We use an **in-process synchronous EventBus** as the primary decoupling mechanism between blackboard subsystems.

### Design

```python
class EventBus:
    def subscribe(self, event_type: str, handler: Callable) -> None
    def publish(self, event_type: str, payload: dict) -> None
    def unsubscribe(self, event_type: str, handler: Callable) -> None
```

- **Synchronous dispatch**: handlers are called inline during `publish()`.
- **No persistence**: events are ephemeral; not stored.
- **String-typed events**: event types are plain strings (e.g., `"artifact.registered"`, `"task.completed"`).

### Event Type Conventions

```
<domain>.<verb>

artifact.registered
artifact.updated
task.registered
task.status_updated
task.completed
agent.started
agent.completed
state.transitioned
```

---

## Consequences

**Positive:**
- Subsystems do not import each other; they only import EventBus.
- Each subsystem can be unit-tested by asserting published events.
- Adding new cross-subsystem behaviors requires only a new subscriber.

**Negative:**
- Synchronous dispatch means a slow handler blocks the publisher.
- Event ordering is implicit (subscription order).
- No replay or persistence for debugging.

**Mitigations:**
- Handlers must be fast (no I/O, no LLM calls).
- Future RC may introduce async dispatch as an opt-in via a wrapper.
