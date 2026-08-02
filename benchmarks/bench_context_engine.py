"""
Benchmark for ContextEngine context assembly under varying artifact scale.
"""

import time
import tracemalloc

from backend.contracts import (
    Artifact,
    ArtifactState,
    ArtifactType,
    DependencyNode,
    Task,
)
from backend.engine import ArtifactRegistry, ContextEngine, DependencyGraph, VersionGraph


def benchmark_context_engine(num_artifacts: int = 1000):
    tracemalloc.start()

    art_reg = ArtifactRegistry()
    dep_graph = DependencyGraph()
    ver_graph = VersionGraph()

    for i in range(num_artifacts):
        art_id = f"art_{i}"
        art = Artifact(
            artifact_id=art_id,
            project_id="proj_1",
            artifact_type=ArtifactType.STORY_OUTLINE,
            owner_agent="StoryAgent",
            title=f"Artifact {i}",
            state=ArtifactState.DRAFT,
            content=f"Sample content for artifact {i}",
        )
        art_reg.register(art)
        dep_graph.add_node(
            DependencyNode(artifact_id=art_id, artifact_type=ArtifactType.STORY_OUTLINE)
        )
        ver_graph.add_version(art_id, version=1, content_hash=f"hash_{i}")

    ctx_engine = ContextEngine(art_reg, dep_graph, ver_graph)
    task = Task(task_id="t1", goal_id="g1", target_agent_type="STORY", description="Benchmark task")

    start_time = time.monotonic()
    bundle = ctx_engine.assemble_context(task)
    duration_ms = (time.monotonic() - start_time) * 1000

    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "benchmark": "ContextEngine",
        "artifacts_in_registry": num_artifacts,
        "assembly_ms": round(duration_ms, 2),
        "token_cost_estimate": bundle.token_count if hasattr(bundle, "token_count") else 0,
        "peak_memory_mb": round(peak_mem / (1024 * 1024), 2),
    }
