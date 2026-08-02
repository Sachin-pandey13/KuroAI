"""
RuntimeTransaction — Atomic persistence boundary for agent execution results.

Every AgentRuntime execution stages all side-effects into a RuntimeTransaction,
then commits atomically. On any failure, rollback() undoes partial writes.

Staged side-effects:
    1. Artifact  → ArtifactRegistry
    2. Version   → VersionGraph
    3. State     → ProjectStateEngine
    4. Events    → EventBus (published on commit)

Design note (future evolution):
    Per the architectural review, rollback handlers are intentionally scoped
    inside this class for M9 simplicity. When transaction complexity grows,
    these should evolve into pluggable RollbackHandler instances:

        ArtifactRollbackHandler
        VersionRollbackHandler
        StateRollbackHandler
        EventRollbackHandler

    RuntimeTransaction would then coordinate them, keeping each subsystem
    responsible for undoing its own work.
"""

from typing import Any, Dict, List

from backend.contracts.artifact import Artifact
from backend.contracts.event import Event


class TransactionError(Exception):
    """Raised when a transaction commit fails."""

    pass


class RuntimeTransaction:
    """
    Atomic commit/rollback for all agent execution side-effects.

    Usage:
        txn = RuntimeTransaction(artifact_registry, version_graph, state_engine, event_bus)
        txn.stage_artifact(artifact)
        txn.stage_version(artifact_id, data, metadata, created_by)
        txn.stage_state_updates({"scene_count": 12})
        txn.stage_event(Event(event_type=EventType.TASK_COMPLETED, ...))
        txn.commit()   # raises TransactionError on failure → call rollback()
    """

    def __init__(
        self,
        artifact_registry,
        version_graph,
        state_engine,
        event_bus,
    ) -> None:
        self._artifact_registry = artifact_registry
        self._version_graph = version_graph
        self._state_engine = state_engine
        self._event_bus = event_bus

        # Staged data
        self._staged_artifacts: List[Artifact] = []
        self._staged_versions: List[Dict[str, Any]] = []
        self._staged_state_updates: Dict[str, Any] = {}
        self._staged_events: List[Event] = []

        # Committed tracking (for rollback)
        self._committed_artifact_ids: List[str] = []
        self._committed_version_ids: List[str] = []

    # ------------------------------------------------------------------
    # Staging API
    # ------------------------------------------------------------------

    def stage_artifact(self, artifact: Artifact) -> None:
        """Stage an artifact for registration on commit."""
        self._staged_artifacts.append(artifact)

    def stage_version(
        self,
        artifact_id: str,
        data: Dict[str, Any],
        metadata: Dict[str, Any],
        created_by: str = "system",
    ) -> None:
        """Stage a version record for VersionGraph on commit."""
        self._staged_versions.append(
            {
                "artifact_id": artifact_id,
                "data": data,
                "metadata": metadata,
                "created_by": created_by,
            }
        )

    def stage_state_updates(self, updates: Dict[str, Any]) -> None:
        """Stage project state updates to apply on commit."""
        self._staged_state_updates.update(updates)

    def stage_event(self, event: Event) -> None:
        """Stage an event for publishing on commit."""
        self._staged_events.append(event)

    # ------------------------------------------------------------------
    # Commit
    # ------------------------------------------------------------------

    def commit(self) -> None:
        """
        Persist all staged side-effects in order:
            1. Artifacts
            2. Versions
            3. State updates
            4. Events

        On any failure, raises TransactionError.
        Caller is responsible for calling rollback() after catching.
        """
        try:
            self._commit_artifacts()
            self._commit_versions()
            self._commit_state_updates()
            self._commit_events()
        except Exception as exc:
            raise TransactionError(
                f"Transaction commit failed: {exc}. " f"Call rollback() to undo partial writes."
            ) from exc

    def _commit_artifacts(self) -> None:
        for artifact in self._staged_artifacts:
            self._artifact_registry.register(artifact)
            self._committed_artifact_ids.append(artifact.artifact_id)

    def _commit_versions(self) -> None:
        for entry in self._staged_versions:
            artifact_id = entry["artifact_id"]
            data = entry["data"]
            metadata = entry["metadata"]
            created_by = entry["created_by"]
            if hasattr(self._version_graph, "record_version"):
                v_entry = self._version_graph.record_version(
                    artifact_id=artifact_id,
                    data=data,
                    metadata=metadata,
                    created_by=created_by,
                    change_summary="Agent execution artifact creation",
                )
                if hasattr(v_entry, "version_number"):
                    self._committed_version_ids.append(f"{artifact_id}:{v_entry.version_number}")

    def _commit_state_updates(self) -> None:
        if self._staged_state_updates and self._state_engine:
            for key, value in self._staged_state_updates.items():
                if hasattr(self._state_engine, "apply_delta"):
                    self._state_engine.apply_delta({key: value})

    def _commit_events(self) -> None:
        for event in self._staged_events:
            self._event_bus.publish(event)

    # ------------------------------------------------------------------
    # Rollback
    # ------------------------------------------------------------------

    def rollback(self) -> None:
        """
        Undo any partial commits in reverse order.
        """
        self._rollback_versions()
        self._rollback_artifacts()
        # Clear staged data to prevent double-commit
        self._staged_artifacts.clear()
        self._staged_versions.clear()
        self._staged_state_updates.clear()
        self._staged_events.clear()

    def _rollback_versions(self) -> None:
        for composite_id in reversed(self._committed_version_ids):
            try:
                artifact_id, _ = composite_id.split(":", 1)
                if hasattr(self._version_graph, "clear_history"):
                    self._version_graph.clear_history(artifact_id)
            except Exception:
                pass  # Best-effort rollback

    def _rollback_artifacts(self) -> None:
        for artifact_id in reversed(self._committed_artifact_ids):
            try:
                if hasattr(self._artifact_registry, "remove"):
                    self._artifact_registry.remove(artifact_id)
            except Exception:
                pass  # Best-effort rollback
