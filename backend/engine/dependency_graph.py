from typing import List, Set, Dict, Optional, Tuple
from datetime import datetime
from collections import deque
from backend.contracts.dependency import DependencyNode, DependencyEdge, EdgeType
from backend.contracts.artifact import ArtifactState, ArtifactType


class CycleDetectedError(Exception):
    """Raised when adding an edge would create a cycle in the DAG."""
    pass


class NodeNotFoundError(Exception):
    """Raised when referencing an artifact node that does not exist in the graph."""
    pass


class EdgeNotFoundError(Exception):
    """Raised when referencing an edge that does not exist in the graph."""
    pass


class DAGAlgorithms:
    """
    Pure graph algorithm helpers (Separation of Graph Structure vs Algorithms).
    """

    @staticmethod
    def detect_cycle(nodes: Dict[str, DependencyNode], edges: Set[Tuple[str, str]]) -> bool:
        """
        Detects if a cycle exists in the directed graph using Kahn's Algorithm / In-degree count.
        Returns True if a cycle exists, False if it's a valid DAG.
        """
        in_degree: Dict[str, int] = {node_id: 0 for node_id in nodes}
        adj: Dict[str, List[str]] = {node_id: [] for node_id in nodes}

        for src, tgt in edges:
            if src in nodes and tgt in nodes:
                adj[src].append(tgt)
                in_degree[tgt] += 1

        queue: deque = deque([n for n, deg in in_degree.items() if deg == 0])
        visited_count = 0

        while queue:
            curr = queue.popleft()
            visited_count += 1
            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return visited_count != len(nodes)

    @staticmethod
    def topological_sort(nodes: Dict[str, DependencyNode], edges: Set[Tuple[str, str]]) -> List[str]:
        """
        Returns a deterministic topological ordering of artifact IDs (execution order).
        Example: Story -> Character -> Prompt -> Image.
        Raises CycleDetectedError if a cycle is present.
        """
        in_degree: Dict[str, int] = {node_id: 0 for node_id in nodes}
        adj: Dict[str, List[str]] = {node_id: [] for node_id in nodes}

        for src, tgt in edges:
            if src in nodes and tgt in nodes:
                adj[src].append(tgt)
                in_degree[tgt] += 1

        # Sort initial nodes deterministically by ID for reproducible ordering
        queue: deque = deque(sorted([n for n, deg in in_degree.items() if deg == 0]))
        topo_order: List[str] = []

        while queue:
            curr = queue.popleft()
            topo_order.append(curr)
            # Sort neighbors for deterministic execution order
            for neighbor in sorted(adj[curr]):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(topo_order) != len(nodes):
            raise CycleDetectedError("Cannot perform topological sort: cycle detected in graph.")

        return topo_order

    @staticmethod
    def get_ancestors(nodes: Dict[str, DependencyNode], artifact_id: str) -> Set[str]:
        """
        Returns all transitive upstream ancestor node IDs for an artifact.
        (e.g., Image ancestors = [Prompt, Character, Story]).
        """
        ancestors: Set[str] = set()
        queue: deque = deque(nodes[artifact_id].upstream_ids)

        while queue:
            curr = queue.popleft()
            if curr not in ancestors and curr in nodes:
                ancestors.add(curr)
                queue.extend(nodes[curr].upstream_ids)

        return ancestors

    @staticmethod
    def get_descendants(nodes: Dict[str, DependencyNode], artifact_id: str) -> Set[str]:
        """
        Returns all transitive downstream descendant node IDs for an artifact.
        (e.g., Story descendants = [Scene, Prompt, Image, Vision Review]).
        """
        descendants: Set[str] = set()
        queue: deque = deque(nodes[artifact_id].downstream_ids)

        while queue:
            curr = queue.popleft()
            if curr not in descendants and curr in nodes:
                descendants.add(curr)
                queue.extend(nodes[curr].downstream_ids)

        return descendants


class DependencyGraph:
    """
    Dependency Graph & Selective Invalidation Engine.
    Enforces the First Law of KuroAI (Incremental Preservation).

    Responsibilities:
    - Maintains DAG structure & edge relationships.
    - Rejects cycles immediately with CycleDetectedError.
    - Provides topological ordering for scheduler execution.
    - Performs selective invalidation: setting descendants STALE while keeping unrelated nodes ACTIVE.
    """

    def __init__(self) -> None:
        self._nodes: Dict[str, DependencyNode] = {}
        self._edges: Set[Tuple[str, str]] = set()  # (source_id, target_id)
        self._edge_metadata: Dict[Tuple[str, str], DependencyEdge] = {}

    # ------------------------------------------------------------------
    # Stage 1 — Graph Structure & Integrity
    # ------------------------------------------------------------------

    def add_node(self, node: DependencyNode) -> None:
        """Add an artifact node to the graph if it doesn't already exist."""
        if node is None:
            return
        if node.artifact_id not in self._nodes:
            self._nodes[node.artifact_id] = node

    def create_node(self, artifact_id: str, artifact_type: str,
                    state: ArtifactState = ArtifactState.ACTIVE) -> DependencyNode:
        """Helper to create and register a new node in one call."""
        node = DependencyNode(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            state=state,
        )
        self.add_node(node)
        return node

    def remove_node(self, artifact_id: str) -> None:
        """
        Remove a node and all associated edges.
        Marks all direct and transitive downstream dependents as INVALID (dependency deleted).
        """
        if artifact_id not in self._nodes:
            raise NodeNotFoundError(f"Node '{artifact_id}' not found in graph.")

        # Invalidate all transitive downstream descendants as INVALID before removal
        descendant_ids = self.descendants(artifact_id)
        for dep_id in descendant_ids:
            if dep_id in self._nodes:
                self._nodes[dep_id].state = ArtifactState.INVALID
                self._nodes[dep_id].invalidation_reason = f"Dependency '{artifact_id}' was deleted."

        # Remove edges connected to this node
        edges_to_remove = [
            (src, tgt) for src, tgt in self._edges
            if src == artifact_id or tgt == artifact_id
        ]
        for src, tgt in edges_to_remove:
            self.remove_edge(src, tgt)

        # Remove the node
        del self._nodes[artifact_id]

    def add_edge(self, edge: DependencyEdge) -> None:
        """
        Add a directed edge: source -> target.
        Validates that both nodes exist and that adding the edge will not create a cycle.
        Raises CycleDetectedError if a cycle is formed.
        """
        src = edge.source_artifact_id
        tgt = edge.target_artifact_id

        if src not in self._nodes:
            raise NodeNotFoundError(f"Source node '{src}' not found in graph.")
        if tgt not in self._nodes:
            raise NodeNotFoundError(f"Target node '{tgt}' not found in graph.")

        edge_tuple = (src, tgt)
        if edge_tuple in self._edges:
            return  # Edge already exists

        # Tentatively add edge and test cycle
        self._edges.add(edge_tuple)
        if DAGAlgorithms.detect_cycle(self._nodes, self._edges):
            self._edges.remove(edge_tuple)
            raise CycleDetectedError(
                f"Adding edge '{src}' -> '{tgt}' creates a cycle in the Dependency Graph."
            )

        # Edge is valid: record metadata and update node relationship pointers
        self._edge_metadata[edge_tuple] = edge
        if tgt not in self._nodes[src].downstream_ids:
            self._nodes[src].downstream_ids.append(tgt)
        if src not in self._nodes[tgt].upstream_ids:
            self._nodes[tgt].upstream_ids.append(src)

    def connect(self, source_id: str, target_id: str,
                edge_type: EdgeType = EdgeType.EXPLICIT) -> None:
        """Convenience method to add an edge between two node IDs."""
        edge = DependencyEdge(
            source_artifact_id=source_id,
            target_artifact_id=target_id,
            edge_type=edge_type,
        )
        self.add_edge(edge)

    def remove_edge(self, source_id: str, target_id: str) -> None:
        """Remove a directed edge between source and target nodes."""
        edge_tuple = (source_id, target_id)
        if edge_tuple not in self._edges:
            return

        self._edges.remove(edge_tuple)
        self._edge_metadata.pop(edge_tuple, None)

        if source_id in self._nodes and target_id in self._nodes[source_id].downstream_ids:
            self._nodes[source_id].downstream_ids.remove(target_id)
        if target_id in self._nodes and source_id in self._nodes[target_id].upstream_ids:
            self._nodes[target_id].upstream_ids.remove(source_id)

    def has_node(self, artifact_id: str) -> bool:
        """Check if node exists in graph."""
        return artifact_id in self._nodes

    def has_edge(self, source_id: str, target_id: str) -> bool:
        """Check if directed edge exists."""
        return (source_id, target_id) in self._edges

    def clear(self) -> None:
        """Clear all nodes and edges from graph."""
        self._nodes.clear()
        self._edges.clear()
        self._edge_metadata.clear()

    # ------------------------------------------------------------------
    # Stage 2 — Graph Validation & Algorithms
    # ------------------------------------------------------------------

    def detect_cycle(self) -> bool:
        """Return True if the graph contains a cycle."""
        return DAGAlgorithms.detect_cycle(self._nodes, self._edges)

    def validate(self) -> bool:
        """Validate graph integrity. Raises CycleDetectedError if invalid."""
        if self.detect_cycle():
            raise CycleDetectedError("Graph contains a cycle.")
        return True

    def topological_sort(self) -> List[str]:
        """Return deterministic execution topological order."""
        return DAGAlgorithms.topological_sort(self._nodes, self._edges)

    # ------------------------------------------------------------------
    # Stage 3 — Traversal
    # ------------------------------------------------------------------

    def get_node(self, artifact_id: str) -> DependencyNode:
        """Fetch node by artifact ID."""
        if artifact_id not in self._nodes:
            raise NodeNotFoundError(f"Node '{artifact_id}' not found.")
        return self._nodes[artifact_id]

    def get_upstream(self, artifact_id: str) -> List[str]:
        """Return immediate parent artifact IDs."""
        return list(self.get_node(artifact_id).upstream_ids)

    def get_downstream(self, artifact_id: str) -> List[str]:
        """Return immediate child artifact IDs."""
        return list(self.get_node(artifact_id).downstream_ids)

    def ancestors(self, artifact_id: str) -> Set[str]:
        """Return all transitive upstream ancestor node IDs."""
        if artifact_id not in self._nodes:
            raise NodeNotFoundError(f"Node '{artifact_id}' not found.")
        return DAGAlgorithms.get_ancestors(self._nodes, artifact_id)

    def descendants(self, artifact_id: str) -> Set[str]:
        """Return all transitive downstream descendant node IDs."""
        if artifact_id not in self._nodes:
            raise NodeNotFoundError(f"Node '{artifact_id}' not found.")
        return DAGAlgorithms.get_descendants(self._nodes, artifact_id)

    # ------------------------------------------------------------------
    # Stage 4 — Selective Invalidation Engine (First Law)
    # ------------------------------------------------------------------

    def invalidate(self, artifact_id: str, reason: str,
                   caused_by_event: Optional[str] = None) -> Set[str]:
        """
        Selective Invalidation Engine (First Law).
        Modifies target node, then recursively sets all downstream descendants to STALE.
        Attaches rich InvalidationRecord containing propagation depth and cause.
        Leaves all unrelated nodes ACTIVE.
        Returns the set of all invalidated (STALE) artifact IDs.
        """
        from backend.contracts.dependency import InvalidationRecord

        if artifact_id not in self._nodes:
            raise NodeNotFoundError(f"Node '{artifact_id}' not found.")

        now = datetime.utcnow()
        source_node = self._nodes[artifact_id]
        source_node.last_invalidated_at = now
        source_node.invalidation_reason = f"Modified: {reason}"
        source_node.last_invalidation_record = InvalidationRecord(
            source_artifact_id=artifact_id,
            affected_artifact_id=artifact_id,
            reason=reason,
            propagation_depth=0,
            caused_by_event=caused_by_event,
            timestamp=now,
        )

        # Compute depth using BFS from source node
        depth_map: Dict[str, int] = {artifact_id: 0}
        queue = deque([artifact_id])
        invalidated: Set[str] = set()

        while queue:
            curr_id = queue.popleft()
            curr_depth = depth_map[curr_id]

            for child_id in self._nodes[curr_id].downstream_ids:
                if child_id in self._nodes:
                    child_depth = curr_depth + 1
                    if child_id not in depth_map or child_depth < depth_map[child_id]:
                        depth_map[child_id] = child_depth
                        queue.append(child_id)

                    node = self._nodes[child_id]
                    node.state = ArtifactState.STALE
                    node.last_invalidated_at = now
                    node.invalidation_reason = f"Upstream '{artifact_id}' was updated ({reason})"
                    node.last_invalidation_record = InvalidationRecord(
                        source_artifact_id=artifact_id,
                        affected_artifact_id=child_id,
                        reason=reason,
                        propagation_depth=depth_map[child_id],
                        caused_by_event=caused_by_event,
                        timestamp=now,
                    )
                    invalidated.add(child_id)

        return invalidated

    def mark_active(self, artifact_id: str) -> None:
        """Mark a node as ACTIVE after successful regeneration."""
        node = self.get_node(artifact_id)
        node.state = ArtifactState.ACTIVE
        node.invalidation_reason = None

    def mark_failed(self, artifact_id: str, reason: str) -> None:
        """Mark a node as FAILED due to execution error."""
        node = self.get_node(artifact_id)
        node.state = ArtifactState.FAILED
        node.invalidation_reason = reason

    # ------------------------------------------------------------------
    # Stage 5 — Dirty Query Subsystem
    # ------------------------------------------------------------------

    def get_dirty(self) -> List[DependencyNode]:
        """Return all nodes currently marked STALE, INVALID, or FAILED."""
        return [
            n for n in self._nodes.values()
            if n.state in (ArtifactState.STALE, ArtifactState.INVALID, ArtifactState.FAILED)
        ]

    def get_dirty_by_type(self, artifact_type: str) -> List[DependencyNode]:
        """Return dirty nodes filtered by artifact type."""
        return [
            n for n in self.get_dirty()
            if n.artifact_type == artifact_type
        ]

    def is_dirty(self, artifact_id: str) -> bool:
        """Return True if node is STALE, INVALID, or FAILED."""
        return self.get_node(artifact_id).state in (
            ArtifactState.STALE, ArtifactState.INVALID, ArtifactState.FAILED
        )

    def clear_dirty(self, artifact_id: str) -> None:
        """Clear dirty status, setting node to ACTIVE."""
        self.mark_active(artifact_id)

    @property
    def node_count(self) -> int:
        """Total node count."""
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        """Total edge count."""
        return len(self._edges)
