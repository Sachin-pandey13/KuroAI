from typing import Optional, Dict, List, Any
from datetime import datetime
from backend.contracts.artifact import Artifact, ArtifactType, ArtifactState
from backend.contracts.event import Event, EventType


class ArtifactNotFoundError(Exception):
    """Raised when an artifact ID does not exist in the registry."""
    pass


class ArtifactAlreadyExistsError(Exception):
    """Raised when attempting to register an artifact with a duplicate ID."""
    pass


class ArtifactRegistry:
    """
    Owns artifact lifecycle: creation, storage, retrieval, metadata updates.
    The ProjectStateEngine references artifacts by ID — it never creates them.

    Lifecycle:
        ArtifactRegistry.register(artifact) → artifact_id
        ProjectStateEngine.attach_artifact(artifact_id) → project state
    """

    def __init__(self, event_bus: Optional[Any] = None) -> None:
        self._store: Dict[str, Artifact] = {}
        self._event_bus = event_bus

    def register(
        self,
        artifact: Artifact,
        version_graph: Optional[Any] = None,
        event_bus: Optional[Any] = None,
    ) -> str:
        """
        Register a new artifact in the registry.
        Atomically records initial V1 in version_graph if provided before publishing ARTIFACT_REGISTERED.
        Returns the artifact_id.
        Raises ArtifactAlreadyExistsError if the ID is already taken.
        """
        if artifact.artifact_id in self._store:
            raise ArtifactAlreadyExistsError(
                f"Artifact '{artifact.artifact_id}' already exists in registry."
            )
        self._store[artifact.artifact_id] = artifact

        # Atomic V1 snapshot in VersionGraph if provided
        if version_graph is not None and not version_graph.has_history(artifact.artifact_id):
            version_graph.record_version(
                artifact_id=artifact.artifact_id,
                data=artifact.data,
                metadata=artifact.metadata,
                created_by=artifact.owner_agent,
                change_summary="Initial artifact creation (V1)",
            )

        # Publish ARTIFACT_REGISTERED event after state & invariants are established
        bus = event_bus or self._event_bus
        if bus is not None:
            artifact_type_val = (
                artifact.artifact_type.value
                if hasattr(artifact.artifact_type, "value")
                else str(artifact.artifact_type)
            )
            bus.publish(
                Event(
                    event_type=EventType.ARTIFACT_REGISTERED,
                    project_id=artifact.project_id,
                    target_artifact_id=artifact.artifact_id,
                    source_agent_id=artifact.owner_agent,
                    payload={"artifact_type": artifact_type_val, "data": artifact.data},
                )
            )

        return artifact.artifact_id

    def get(self, artifact_id: str) -> Artifact:
        """
        Fetch an artifact by UUID.
        Raises ArtifactNotFoundError if not found.
        """
        if artifact_id not in self._store:
            raise ArtifactNotFoundError(
                f"Artifact '{artifact_id}' not found in registry."
            )
        return self._store[artifact_id]

    def exists(self, artifact_id: str) -> bool:
        """Check whether an artifact ID is registered."""
        return artifact_id in self._store

    def update_metadata(self, artifact_id: str, metadata: Dict[str, Any]) -> Artifact:
        """
        Merge new metadata into an existing artifact.
        Returns the updated artifact.
        Raises ArtifactNotFoundError if not found.
        """
        artifact = self.get(artifact_id)
        artifact.metadata.update(metadata)
        artifact.updated_at = datetime.utcnow()
        if self._event_bus:
            self._event_bus.publish(
                Event(
                    event_type=EventType.ARTIFACT_UPDATED,
                    project_id=artifact.project_id,
                    target_artifact_id=artifact.artifact_id,
                    source_agent_id=artifact.owner_agent,
                    payload={"metadata": artifact.metadata, "data": artifact.data},
                )
            )
        return artifact

    def update_data(self, artifact_id: str, data: Dict[str, Any]) -> Artifact:
        """
        Update the data payload of an artifact.
        Returns the updated artifact.
        """
        artifact = self.get(artifact_id)
        artifact.data.update(data)
        artifact.updated_at = datetime.utcnow()
        if self._event_bus:
            self._event_bus.publish(
                Event(
                    event_type=EventType.ARTIFACT_UPDATED,
                    project_id=artifact.project_id,
                    target_artifact_id=artifact.artifact_id,
                    source_agent_id=artifact.owner_agent,
                    payload={"data": artifact.data, "metadata": artifact.metadata},
                )
            )
        return artifact

    def update_state(self, artifact_id: str, state: ArtifactState) -> Artifact:
        """Update the lifecycle state of an artifact."""
        artifact = self.get(artifact_id)
        artifact.state = state
        artifact.updated_at = datetime.utcnow()
        return artifact

    def update_status(self, artifact_id: str, status: ArtifactState) -> Artifact:
        """Alias for update_state."""
        return self.update_state(artifact_id, status)

    def list_by_type(self, artifact_type: ArtifactType) -> List[Artifact]:
        """List all artifacts matching an ArtifactType."""
        return [
            a for a in self._store.values()
            if a.artifact_type == artifact_type
        ]

    def list_by_project(self, project_id: str) -> List[Artifact]:
        """List all artifacts belonging to a project."""
        return [
            a for a in self._store.values()
            if a.project_id == project_id
        ]

    def list_all(self) -> List[Artifact]:
        """Return all registered artifacts."""
        return list(self._store.values())

    def remove(self, artifact_id: str) -> Artifact:
        """
        Remove an artifact from the registry.
        Returns the removed artifact.
        Raises ArtifactNotFoundError if not found.
        """
        if artifact_id not in self._store:
            raise ArtifactNotFoundError(
                f"Artifact '{artifact_id}' not found in registry."
            )
        return self._store.pop(artifact_id)

    def register_listeners(self, bus: Any) -> None:
        """Register ArtifactRegistry reactions on the EventBus."""
        bus.subscribe(EventType.ARTIFACT_ROLLED_BACK, self._on_artifact_rolled_back)

    def unregister_listeners(self, bus: Any) -> None:
        """Unregister ArtifactRegistry reactions from the EventBus."""
        bus.unsubscribe(EventType.ARTIFACT_ROLLED_BACK, self._on_artifact_rolled_back)

    def _on_artifact_rolled_back(self, event: Event) -> None:
        """React to ARTIFACT_ROLLED_BACK by restoring internal artifact payload."""
        artifact_id = event.target_artifact_id
        if artifact_id and self.exists(artifact_id):
            artifact = self.get(artifact_id)
            if "data" in event.payload:
                artifact.data = dict(event.payload["data"])
            if "metadata" in event.payload:
                artifact.metadata = dict(event.payload["metadata"])
            if "version_number" in event.payload:
                artifact.current_version = event.payload["version_number"]
            artifact.updated_at = datetime.utcnow()

    @property
    def count(self) -> int:
        """Return the total number of registered artifacts."""
        return len(self._store)

