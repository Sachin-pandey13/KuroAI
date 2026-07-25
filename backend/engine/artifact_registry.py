from typing import Optional, Dict, List, Any
from backend.contracts.artifact import Artifact, ArtifactType


class ArtifactRegistry:
    """
    Manages first-class artifact registration, retrieval, and indexing.
    """

    def __init__(self):
        pass

    def register_artifact(self, artifact: Artifact) -> None:
        """Register a new artifact."""
        raise NotImplementedError("ArtifactRegistry.register_artifact stub")

    def get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        """Fetch artifact by UUID."""
        raise NotImplementedError("ArtifactRegistry.get_artifact stub")

    def list_by_type(self, artifact_type: ArtifactType) -> List[Artifact]:
        """List all artifacts matching an ArtifactType."""
        raise NotImplementedError("ArtifactRegistry.list_by_type stub")
