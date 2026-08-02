"""
Benchmark suite runner and performance report generator.
Exports reports in Markdown, JSON, and CSV formats and archives historical runs.
"""

import csv
import gc
import json
import os
import sys
import time
from typing import Any, Dict, List

from benchmarks.bench_context_engine import benchmark_context_engine
from benchmarks.bench_dependency_graph import benchmark_dependency_graph
from benchmarks.bench_scheduler_runtime import benchmark_scheduler


def run_benchmark_suite() -> List[Dict[str, Any]]:
    results = []
    gc_before = gc.get_count()

    print("Running DependencyGraph scale benchmark...")
    res_dep = benchmark_dependency_graph(num_nodes=5000, num_edges=10000)
    results.append(res_dep)

    print("Running ContextEngine assembly benchmark...")
    res_ctx = benchmark_context_engine(num_artifacts=1000)
    results.append(res_ctx)

    print("Running TaskScheduler throughput benchmark...")
    res_sched = benchmark_scheduler(num_tasks=1000)
    results.append(res_sched)

    gc_after = gc.get_count()
    gc_collections = [after - before for before, after in zip(gc_before, gc_after)]

    for r in results:
        r["gc_collections"] = gc_collections

    return results


def export_reports(results: List[Dict[str, Any]]) -> None:
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
    history_dir = os.path.join("benchmarks", "history")
    os.makedirs(history_dir, exist_ok=True)

    # 1. Markdown Report
    md_lines = [
        "# KuroAI Performance Benchmark Report",
        "",
        f"**Generated at:** {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}",
        f"**Python Version:** {sys.version.split()[0]}",
        "",
        "## Summary Results",
        "",
        "| Benchmark | Metric | Peak Memory (MB) |",
        "|---|---|---|",
    ]
    for r in results:
        name = r["benchmark"]
        if name == "DependencyGraph":
            val = f"Nodes: {r['nodes']}, Edges: {r['edges']} (Cycle: {r['cycle_detect_ms']}ms)"
        elif name == "ContextEngine":
            val = f"Artifacts: {r['artifacts_in_registry']} (Assembly: {r['assembly_ms']}ms)"
        elif name == "TaskScheduler":
            val = f"Tasks: {r['tasks_scheduled']} (Dispatch: {r['dispatch_ms']}ms)"
        else:
            val = "N/A"
        md_lines.append(f"| {name} | {val} | {r.get('peak_memory_mb', 0)} MB |")

    with open("performance_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print("[SUCCESS] Exported performance_report.md")

    # 2. JSON Report
    json_path = os.path.join("benchmarks", "performance.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"timestamp": timestamp, "results": results}, f, indent=2)
    print(f"[SUCCESS] Exported {json_path}")

    # 3. CSV Report
    csv_path = os.path.join("benchmarks", "performance.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["benchmark", "metric", "peak_memory_mb"])
        for r in results:
            name = r["benchmark"]
            writer.writerow([name, str(r), r.get("peak_memory_mb", 0)])
    print(f"[SUCCESS] Exported {csv_path}")

    # 4. Archive to history/
    archive_path = os.path.join(history_dir, f"run_{timestamp}.json")
    with open(archive_path, "w", encoding="utf-8") as f:
        json.dump({"timestamp": timestamp, "results": results}, f, indent=2)
    print(f"[SUCCESS] Archived run to {archive_path}")


if __name__ == "__main__":
    res = run_benchmark_suite()
    export_reports(res)
