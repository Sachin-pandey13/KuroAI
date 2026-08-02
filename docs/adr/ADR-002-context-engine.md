# ADR-002 — Context Engine Design

**Date:** 2026-08-02
**Status:** Accepted
**Authors:** KuroAI Architecture Team

---

## Context

KuroAI's agents need rich context to make decisions: what artifacts exist, what their current state is, what depends on what, and what version is current. Without a structured assembly process, each agent would independently query the blackboard — duplicating logic and creating implicit coupling to the engine layer.

---

## Decision

We introduce `ContextEngine` as the **single entry point** for assembling a `ContextBundle` before any agent execution.

### Design

```python
class ContextEngine:
    def assemble_context(self, task: Task) -> ContextBundle
    def register_section_provider(self, selector: ContextSelector, retriever: BaseRetriever) -> None
```

- `assemble_context()` queries `ArtifactRegistry`, `DependencyGraph`, `VersionGraph` and merges results into a single `ContextBundle`.
- `register_section_provider()` allows extending the context with domain-specific retrievers (e.g., a retriever that adds screenplay formatting rules to context for screenplay agents).
- `ContextBundle` is a frozen Pydantic model — immutable once assembled.
- `ContextSelector` is an enum — guards against typo-based bugs in provider registration.

### Flow

```
Task → ContextEngine.assemble_context()
    → BaseRetriever(s) per ContextSelector
    → ContextBundle (immutable)
    → Agent.execute(context_bundle)
```

---

## Consequences

**Positive:**
- Agents are decoupled from all blackboard subsystems — they only receive a `ContextBundle`.
- Context assembly is testable in isolation.
- New context sections can be added without modifying any agent.

**Negative:**
- `ContextEngine` accumulates dependencies on multiple engine subsystems.
- Context is assembled on every task — no caching. (Intentional for RC-1 correctness.)

**Future:**
- RC-2 may introduce selective context assembly (only fetch sections relevant to the agent's `agent_type`).
- Caching of unchanged context sections may be introduced with a hash-based invalidation strategy.
