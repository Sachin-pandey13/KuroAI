"""
Stress test for DependencyGraph scale operations.
"""

import pytest
from backend.contracts import DependencyNode, ArtifactType
from backend.engine.dependency_graph import DependencyGraph


def test_large_dag_scale():
    graph = DependencyGraph()
    num_nodes = 2000

    for i in range(num_nodes):
        graph.add_node(DependencyNode(artifact_id=f"node_{i}", artifact_type=ArtifactType.STORY_OUTLINE))

    for i in range(num_nodes - 1):
        graph.add_edge(f"node_{i}", f"node_{i+1}")

    assert not graph.detect_cycles()
    deps = graph.get_dependencies("node_0")
    assert isinstance(deps, list)
