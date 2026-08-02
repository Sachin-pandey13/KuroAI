"""
Benchmark for DependencyGraph scale (node/edge addition, BFS traversal, cycle detection).
"""

import time
import tracemalloc

from backend.contracts import ArtifactType, DependencyNode
from backend.engine.dependency_graph import DependencyGraph


def benchmark_dependency_graph(num_nodes: int = 5000, num_edges: int = 10000):
    tracemalloc.start()
    start_time = time.monotonic()

    graph = DependencyGraph()
    for i in range(num_nodes):
        graph.add_node(
            DependencyNode(artifact_id=f"art_{i}", artifact_type=ArtifactType.STORY_OUTLINE)
        )

    for i in range(num_edges):
        from_id = f"art_{i % (num_nodes - 1)}"
        to_id = f"art_{(i + 1) % num_nodes}"
        try:
            graph.add_edge(from_id, to_id)
        except Exception:
            pass

    t1 = time.monotonic()
    add_duration_ms = (t1 - start_time) * 1000

    graph.detect_cycles()
    t2 = time.monotonic()
    cycle_duration_ms = (t2 - t1) * 1000

    graph.get_dependencies("art_0")
    t3 = time.monotonic()
    bfs_duration_ms = (t3 - t2) * 1000

    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "benchmark": "DependencyGraph",
        "nodes": num_nodes,
        "edges": num_edges,
        "build_ms": round(add_duration_ms, 2),
        "cycle_detect_ms": round(cycle_duration_ms, 2),
        "bfs_ms": round(bfs_duration_ms, 2),
        "peak_memory_mb": round(peak_mem / (1024 * 1024), 2),
    }
