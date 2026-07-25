from typing import Optional, Dict, List, Any
from datetime import datetime
from backend.contracts.artifact import Artifact, ArtifactType, ArtifactStatus


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

    def __init__(self) -> None:
        self._store: Dict[str, Artifact] = {}

    def register(self, artifact: Artifact) -> str:
        """
        Register a new artifact in the registry.
        Returns the artifact_id.
        Raises ArtifactAlreadyExistsError if the ID is already taken.
        """
        if artifact.artifact_id in self._store:
            raise ArtifactAlreadyExistsError(
                f"Artifact '{artifact.artifact_id}' already exists in registry."
            )
        self._store[artifact.artifact_id] = artifact
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
        return artifact

    def update_data(self, artifact_id: str, data: Dict[str, Any]) -> Artifact:
        """
        Update the data payload of an artifact.
        Returns the updated artifact.
        """
        artifact = self.get(artifact_id)
        artifact.data.update(data)
        artifact.updated_at = datetime.utcnow()
        return artifact

    def update_status(self, artifact_id: str, status: ArtifactStatus) -> Artifact:
        """Update the lifecycle status of an artifact."""
        artifact = self.get(artifact_id)
        artifact.status = status
        artifact.updated_at = datetime.utcnow()
        return artifact

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

    @property
    def count(self) -> int:
        """Return the total number of registered artifacts."""
        return len(self._store)
