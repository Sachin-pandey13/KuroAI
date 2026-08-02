# ADR-004 — Human Review Integration

**Date:** 2026-08-02
**Status:** Proposed (RC-2 scope)
**Authors:** KuroAI Architecture Team

---

## Context

KuroAI is a generative AI pipeline that produces creative artifacts (story plans, scenes, images). Some output may require human review before proceeding to downstream steps. Without a structured review gate, either:

1. All output proceeds automatically (risk of cascading bad generations), or
2. All output pauses for manual intervention (blocks automation).

A structured human review mechanism allows selective, policy-driven review gates.

---

## Decision (Proposed for RC-2)

Introduce a `HumanReviewGate` as a first-class subsystem alongside `AgentRuntime`.

### Design (Proposed)

```python
class HumanReviewGate:
    def requires_review(self, artifact: Artifact, policy: ReviewPolicy) -> bool
    async def request_review(self, artifact: Artifact) -> ReviewDecision
    def auto_approve(self, artifact: Artifact) -> ReviewDecision
```

`ReviewDecision` is an enum: `APPROVED`, `REJECTED`, `REVISION_REQUESTED`.

### Integration Point

`AgentRuntime.run_task()` will check `HumanReviewGate.requires_review()` after `agent.execute()` and before `artifact_registry.update()`:

```
... agent.execute(task, context) → AgentResult
    → if review_gate.requires_review(result.artifact, policy):
        → decision = await review_gate.request_review(result.artifact)
        → if decision == REJECTED: raise AgentRuntimeError
        → if decision == REVISION_REQUESTED: re-queue task
    → artifact_registry.update(result.artifact)
```

### Review Policies

```python
class ReviewPolicy(Enum):
    NEVER = "never"           # fully automated
    ALWAYS = "always"         # always require review
    ON_CONFIDENCE_LOW = "on_confidence_low"   # review if agent confidence < threshold
    ON_FIRST_DRAFT = "on_first_draft"         # review only version 1 of each artifact
```

---

## Status: RC-1 Stub

For RC-1, `HumanReviewGate` is **not implemented**. The `AgentRuntime` has a placeholder `_human_review` attribute set to `None`, which future RC-2 work can populate.

The architecture is designed so that inserting the gate requires modifying only `AgentRuntime.run_task()` — no other classes need to change.

---

## Consequences

**Positive:**
- Human review is a first-class concept, not bolted on later.
- Policies make review behavior explicit and configurable.
- Selective review avoids blocking the entire pipeline.

**Negative:**
- Async review introduces latency in the pipeline.
- RC-2 must design the notification/callback mechanism (WebSocket? polling?).

**Open Questions (for RC-2):**
1. How does a human reviewer submit a decision? (API endpoint? CLI? Web UI?)
2. How long should the system wait before auto-approving (timeout policy)?
3. Should rejected artifacts be automatically re-queued or require manual restart?
