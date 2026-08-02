import copy
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.contracts.event import Event, EventType
from backend.contracts.version import DiffResult, VersionEntry
from backend.engine.artifact_registry import ArtifactRegistry
from backend.engine.dependency_graph import DependencyGraph


class VersionNotFoundError(Exception):
    """Raised when a specific version number does not exist for an artifact."""

    pass


class ArtifactHistoryNotFoundError(Exception):
    """Raised when requesting version history for an artifact that has no recorded versions."""

    pass


class InvalidVersionError(Exception):
    """Raised when an invalid version parameter is supplied."""

    pass


class VersionGraph:
    """
    Per-Node Version Graph & Editability Engine (Third Law).

    Responsibilities:
    - Maintains independent, immutable version timelines per artifact.
    - Performs non-destructive rollbacks (extending history, never deleting).
    - Computes structural field-by-field diffs between any two version snapshots.
    - Emits ARTIFACT_ROLLED_BACK event after rollback operations complete.
    """

    def __init__(self, event_bus: Optional[Any] = None) -> None:
        # artifact_id -> List[VersionEntry] ordered by version_number (1-indexed)
        self._timelines: Dict[str, List[VersionEntry]] = {}
        self._event_bus = event_bus

    # ------------------------------------------------------------------
    # Stage 2 — Version Graph Core Operations
    # ------------------------------------------------------------------

    def add_version(
        self, artifact_id: str, version: int = 1, content_hash: str = ""
    ) -> VersionEntry:
        """Public API Alias for record_version."""
        return self.record_version(
            artifact_id, {"content_hash": content_hash}, {"version": version}
        )

    def record_version(
        self,
        artifact_id: str,
        data: Dict[str, Any],
        metadata: Dict[str, Any],
        created_by: str = "system",
        change_summary: Optional[str] = None,
        parent_version: Optional[int] = None,
        rollback_of: Optional[int] = None,
        trigger_event: Optional[str] = None,
    ) -> VersionEntry:
        """
        Record a new immutable version snapshot for an artifact node.
        Auto-increments version_number sequentially (1, 2, 3...).
        Deep-copies data and metadata snapshots for immutability.
        """
        if artifact_id not in self._timelines:
            self._timelines[artifact_id] = []

        timeline = self._timelines[artifact_id]
        next_version_num = len(timeline) + 1

        if parent_version is None and timeline:
            parent_version = timeline[-1].version_number

        entry = VersionEntry(
            artifact_id=artifact_id,
            version_number=next_version_num,
            parent_version=parent_version,
            rollback_of=rollback_of,
            trigger_event=trigger_event,
            data_snapshot=copy.deepcopy(data),
            metadata_snapshot=copy.deepcopy(metadata),
            created_by=created_by,
            change_summary=change_summary,
            created_at=datetime.utcnow(),
        )

        timeline.append(entry)
        return entry

    def get_latest(self, artifact_id: str) -> VersionEntry:
        """Fetch the current HEAD version snapshot for an artifact."""
        if not self.has_history(artifact_id):
            raise ArtifactHistoryNotFoundError(
                f"No version history found for artifact '{artifact_id}'."
            )
        return self._timelines[artifact_id][-1]

    def get_latest_version(self, artifact_id: str) -> VersionEntry:
        """Public API Alias for get_latest."""
        return self.get_latest(artifact_id)

    def get_version(self, artifact_id: str, version_number: int) -> VersionEntry:
        """Fetch a specific historical version snapshot by version number."""
        if not self.has_history(artifact_id):
            raise ArtifactHistoryNotFoundError(
                f"No version history found for artifact '{artifact_id}'."
            )

        timeline = self._timelines[artifact_id]
        if version_number < 1 or version_number > len(timeline):
            raise VersionNotFoundError(
                f"Version {version_number} does not exist for artifact '{artifact_id}'. "
                f"Available versions: 1..{len(timeline)}."
            )
        return timeline[version_number - 1]

    def get_history(self, artifact_id: str) -> List[VersionEntry]:
        """Return the complete ordered version history timeline for an artifact."""
        if not self.has_history(artifact_id):
            raise ArtifactHistoryNotFoundError(
                f"No version history found for artifact '{artifact_id}'."
            )
        return list(self._timelines[artifact_id])

    def has_history(self, artifact_id: str) -> bool:
        """Return True if the artifact has recorded versions."""
        return artifact_id in self._timelines and len(self._timelines[artifact_id]) > 0

    def clear_history(self, artifact_id: str) -> None:
        """Remove version history timeline for an artifact."""
        self._timelines.pop(artifact_id, None)

    # ------------------------------------------------------------------
    # Stage 3 — Non-Destructive Rollback Engine
    # ------------------------------------------------------------------

    def rollback(
        self,
        artifact_id: str,
        target_version: int,
        created_by: str = "human_director",
        reason: Optional[str] = None,
        event_bus: Optional[Any] = None,
        project_id: str = "default_project",
    ) -> VersionEntry:
        """
        Non-Destructive Rollback (Third Law).

        Rules:
        1. Rollback NEVER deletes versions from history.
        2. Policy for Rollback to HEAD: If target_version == current HEAD version,
           return the current HEAD version without appending a redundant version entry.
        3. For target_version != current HEAD: Create a new version VN+1 containing
           the restored contents of target_version, with rollback_of=target_version.
        4. Publishes ARTIFACT_ROLLED_BACK event after rollback state is persisted.
        """
        latest = self.get_latest(artifact_id)

        if target_version < 1 or target_version > len(self._timelines[artifact_id]):
            raise VersionNotFoundError(
                f"Cannot rollback artifact '{artifact_id}': Target version {target_version} invalid."
            )

        # Rollback HEAD policy: no-op if target is already the current HEAD
        if target_version == latest.version_number:
            return latest

        target_snapshot = self.get_version(artifact_id, target_version)

        summary = reason or f"Rollback to Version {target_version}"
        new_version = self.record_version(
            artifact_id=artifact_id,
            data=target_snapshot.data_snapshot,
            metadata=target_snapshot.metadata_snapshot,
            created_by=created_by,
            change_summary=summary,
            parent_version=latest.version_number,
            rollback_of=target_version,
        )

        bus = event_bus or self._event_bus
        if bus is not None:
            bus.publish(
                Event(
                    event_type=EventType.ARTIFACT_ROLLED_BACK,
                    project_id=project_id,
                    target_artifact_id=artifact_id,
                    source_agent_id=created_by,
                    payload={
                        "target_version": target_version,
                        "version_number": new_version.version_number,
                        "data": new_version.data_snapshot,
                        "metadata": new_version.metadata_snapshot,
                        "reason": summary,
                    },
                )
            )

        return new_version

    # ------------------------------------------------------------------
    # Stage 4 — Structural Version Diff Engine
    # ------------------------------------------------------------------

    def diff(self, artifact_id: str, version_a: int, version_b: int) -> DiffResult:
        """
        Computes a structural field-by-field comparison of artifact payloads between version_a and version_b.
        """
        snap_a = self.get_version(artifact_id, version_a).data_snapshot
        snap_b = self.get_version(artifact_id, version_b).data_snapshot

        all_keys = set(snap_a.keys()).union(set(snap_b.keys()))

        added: Dict[str, Any] = {}
        removed: Dict[str, Any] = {}
        modified: Dict[str, Dict[str, Any]] = {}
        unchanged: List[str] = []

        for key in sorted(all_keys):
            if key not in snap_a:
                added[key] = copy.deepcopy(snap_b[key])
            elif key not in snap_b:
                removed[key] = copy.deepcopy(snap_a[key])
            elif snap_a[key] != snap_b[key]:
                modified[key] = {
                    "old": copy.deepcopy(snap_a[key]),
                    "new": copy.deepcopy(snap_b[key]),
                }
            else:
                unchanged.append(key)

        return DiffResult(
            artifact_id=artifact_id,
            version_a=version_a,
            version_b=version_b,
            added=added,
            removed=removed,
            modified=modified,
            unchanged=unchanged,
        )

    # ------------------------------------------------------------------
    # Stage 5 — Subsystem Integration Helper & Event Listeners
    # ------------------------------------------------------------------

    def rollback_and_invalidate(
        self,
        artifact_id: str,
        target_version: int,
        artifact_registry: ArtifactRegistry,
        dependency_graph: DependencyGraph,
        created_by: str = "human_director",
        reason: Optional[str] = None,
        event_bus: Optional[Any] = None,
    ) -> VersionEntry:
        """
        Integrated Rollback Helper:
        1. Executes non-destructive rollback in VersionGraph (publishing ARTIFACT_ROLLED_BACK if bus present).
        2. Updates payload and version in ArtifactRegistry.
        3. Triggers DependencyGraph invalidation, recursively marking downstream nodes STALE.
        """
        rollback_reason = reason or f"Rollback to Version {target_version}"

        # Determine project_id if artifact exists
        project_id = "default_project"
        if artifact_registry.exists(artifact_id):
            project_id = artifact_registry.get(artifact_id).project_id

        # 1. Rollback in Version Graph
        new_version = self.rollback(
            artifact_id=artifact_id,
            target_version=target_version,
            created_by=created_by,
            reason=rollback_reason,
            event_bus=event_bus,
            project_id=project_id,
        )

        # 2. Update Artifact Registry (if listeners didn't do it via bus)
        if artifact_registry.exists(artifact_id):
            artifact = artifact_registry.get(artifact_id)
            artifact.data = copy.deepcopy(new_version.data_snapshot)
            artifact.metadata = copy.deepcopy(new_version.metadata_snapshot)
            artifact.current_version = new_version.version_number
            artifact.updated_at = datetime.utcnow()

        # 3. Invalidate Downstream Dependents in Dependency Graph (if listeners didn't do it)
        if dependency_graph.has_node(artifact_id):
            dependency_graph.invalidate(artifact_id, reason=rollback_reason)

        return new_version

    def register_listeners(self, bus: Any) -> None:
        """Register VersionGraph reactions on the EventBus."""
        bus.subscribe(EventType.ARTIFACT_UPDATED, self._on_artifact_updated)

    def unregister_listeners(self, bus: Any) -> None:
        """Unregister VersionGraph reactions from the EventBus."""
        bus.unsubscribe(EventType.ARTIFACT_UPDATED, self._on_artifact_updated)

    def _on_artifact_updated(self, event: Event) -> None:
        """Auto-record a new version snapshot when an ARTIFACT_UPDATED event is received."""
        artifact_id = event.target_artifact_id
        if artifact_id:
            data = event.payload.get("data", {})
            metadata = event.payload.get("metadata", {})
            created_by = event.source_agent_id or "system"
            summary = event.payload.get("change_summary", "Auto-recorded update")
            self.record_version(
                artifact_id=artifact_id,
                data=data,
                metadata=metadata,
                created_by=created_by,
                change_summary=summary,
            )
