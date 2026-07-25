from typing import List, Set, Optional
from backend.contracts.dependency import DependencyNode, DependencyEdge
from backend.contracts.artifact import ArtifactState


class DependencyGraph:
    """
    Directed Acyclic Graph (DAG) tracking artifact dependencies.
    Supports selective downstream invalidation (First Law).
    Every artifact is a node. Every relationship is an edge.
    """

    def __init__(self):
        pass

    def add_node(self, node: DependencyNode) -> None:
        """Register an artifact as a DAG node."""
        raise NotImplementedError("DependencyGraph.add_node stub")

    def add_edge(self, edge: DependencyEdge) -> None:
        """Create a dependency relationship between two artifact nodes."""
        raise NotImplementedError("DependencyGraph.add_edge stub")

    def remove_node(self, artifact_id: str) -> None:
        """Remove a node and its edges from the graph."""
        raise NotImplementedError("DependencyGraph.remove_node stub")

    def get_node(self, artifact_id: str) -> Optional[DependencyNode]:
        """Retrieve a node by artifact ID."""
        raise NotImplementedError("DependencyGraph.get_node stub")

    def get_upstream(self, artifact_id: str) -> List[DependencyNode]:
        """Return all direct upstream dependencies of a node."""
        raise NotImplementedError("DependencyGraph.get_upstream stub")

    def get_downstream(self, artifact_id: str) -> List[DependencyNode]:
        """Return all direct downstream dependents of a node."""
        raise NotImplementedError("DependencyGraph.get_downstream stub")

    def invalidate(self, artifact_id: str, reason: str) -> Set[str]:
        """
        Mark a node DIRTY and propagate invalidation to all downstream dependents.
        Returns the set of all invalidated artifact IDs.
        """
        raise NotImplementedError("DependencyGraph.invalidate stub")

    def get_all_dirty(self) -> List[DependencyNode]:
        """Return all nodes currently marked DIRTY."""
        raise NotImplementedError("DependencyGraph.get_all_dirty stub")

    def mark_clean(self, artifact_id: str) -> None:
        """Mark a node as CLEAN after successful regeneration."""
        raise NotImplementedError("DependencyGraph.mark_clean stub")

    def validate_acyclic(self) -> bool:
        """Verify the graph contains no cycles."""
        raise NotImplementedError("DependencyGraph.validate_acyclic stub")
