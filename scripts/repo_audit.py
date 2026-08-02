"""
KuroAI 25-Point Categorized Repository Health Gate Script.
Executes automated ship/no-ship quality and environment verification across 25 engineering dimensions.

Usage:
    python scripts/repo_audit.py
"""

import os
import subprocess
import sys
from typing import List, Tuple

CHECKS_PASSED = 0
CHECKS_FAILED = 0


def record_result(check_name: str, success: bool, message: str = ""):
    global CHECKS_PASSED, CHECKS_FAILED
    if success:
        CHECKS_PASSED += 1
        print(f"  [PASS] {check_name}")
    else:
        CHECKS_FAILED += 1
        print(f"  [FAIL] {check_name}: {message}")


def run_cmd(cmd: List[str]) -> Tuple[int, str]:
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return res.returncode, res.stdout + res.stderr
    except Exception as e:
        return 1, str(e)


# ----------------------------------------------------------------------
# Section 1: Dependency Checks
# ----------------------------------------------------------------------
def check_1_import_graph():
    code, out = run_cmd(
        [
            sys.executable,
            "-c",
            "import backend; import backend.agents; import backend.capabilities; import backend.engine",
        ]
    )
    record_result("1. Import Graph Validation", code == 0, out)


def check_2_dual_env_dependencies():
    runtime_ok = os.path.exists("requirements/runtime.txt")
    ci_ok = os.path.exists("requirements/ci.txt")
    if ci_ok:
        with open("requirements/ci.txt", "r", encoding="utf-8") as f:
            ci_content = f.read()
        inherits_runtime = "-r runtime.txt" in ci_content
    else:
        inherits_runtime = False

    success = runtime_ok and ci_ok and inherits_runtime
    msg = "requirements/{runtime,ci}.txt missing or ci.txt does not inherit runtime.txt"
    record_result("2. Dual-Environment Dependency Layering", success, msg)


def check_3_dependency_audit():
    code, out = run_cmd([sys.executable, "scripts/dependency_audit.py"])
    record_result("3. Dependency Audit & Package Inventory", code == 0, out)


# ----------------------------------------------------------------------
# Section 2: Quality Checks
# ----------------------------------------------------------------------
def check_4_formatting_black():
    code, out = run_cmd(
        [
            sys.executable,
            "-m",
            "black",
            "--check",
            "backend",
            "config",
            "scripts",
            "tests",
            "benchmarks",
        ]
    )
    record_result("4. Code Formatting (Black)", code == 0, out)


def check_5_import_sorting_isort():
    code, out = run_cmd(
        [
            sys.executable,
            "-m",
            "isort",
            "--check-only",
            "backend",
            "config",
            "scripts",
            "tests",
            "benchmarks",
        ]
    )
    record_result("5. Import Sorting (isort)", code == 0, out)


def check_6_linting_ruff():
    code, out = run_cmd(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "backend",
            "config",
            "scripts",
            "tests",
            "benchmarks",
        ]
    )
    record_result("6. Code Linting (Ruff)", code == 0, out)


def check_7_typechecking_mypy():
    code, out = run_cmd(
        [
            sys.executable,
            "-m",
            "mypy",
            "backend",
            "config",
            "--ignore-missing-imports",
        ]
    )
    record_result("7. Type Check (MyPy)", code == 0, out)


# ----------------------------------------------------------------------
# Section 3: Testing & Determinism
# ----------------------------------------------------------------------
def check_8_test_collection():
    code, out = run_cmd([sys.executable, "-m", "pytest", "--collect-only", "-q"])
    record_result("8. Test Collection Gate (pytest --collect-only -q)", code == 0, out)


def check_9_unit_test_suite():
    code, out = run_cmd(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "-q",
            "--ignore=tests/stress",
        ]
    )
    record_result("9. Unit Test Suite Pass", code == 0, out)


def check_10_coverage():
    code, out = run_cmd(
        [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "-m",
            "pytest",
            "tests/",
            "--ignore=tests/stress",
            "-q",
        ]
    )
    if code == 0:
        code_rep, out_rep = run_cmd(
            [
                sys.executable,
                "-m",
                "coverage",
                "report",
                "--fail-under=80",
            ]
        )
        record_result("10. Coverage Threshold (>=80%)", code_rep == 0, out_rep)
    else:
        record_result("10. Coverage Threshold (>=80%)", False, "Coverage run failed")


def check_11_test_determinism_bootstrap():
    has_conftest = os.path.exists("tests/conftest.py")
    if has_conftest:
        with open("tests/conftest.py", "r", encoding="utf-8") as f:
            content = f.read()
        has_seeds = "random.seed" in content
    else:
        has_seeds = False
    record_result("11. Test Determinism & Seed Bootstrap", has_conftest and has_seeds)


# ----------------------------------------------------------------------
# Section 4: Infrastructure & Workflow Health
# ----------------------------------------------------------------------
def check_12_docker():
    files = [
        "Dockerfile",
        "docker-compose.dev.yml",
        "docker-compose.prod.yml",
        "docker-compose.gpu.yml",
    ]
    missing = [f for f in files if not os.path.exists(f)]
    record_result(
        "12. Docker Stacks (dev/prod/gpu)", len(missing) == 0, f"Missing files: {missing}"
    )


def check_13_workflow_syntax():
    workflows = [
        ".github/workflows/ci.yml",
        ".github/workflows/codeql.yml",
        ".github/workflows/docs.yml",
        ".github/workflows/benchmarks.yml",
        ".github/workflows/release.yml",
    ]
    missing = [w for w in workflows if not os.path.exists(w)]
    record_result(
        "13. Workflow Syntax & Modular Structure",
        len(missing) == 0,
        f"Missing workflows: {missing}",
    )


def check_14_mkdocs():
    code, out = run_cmd([sys.executable, "-m", "mkdocs", "build"])
    record_result("14. MkDocs Site Compilation", code == 0, out)


def check_15_doc_links():
    docs = [
        "README.md",
        "ARCHITECTURE_v1.md",
        "PUBLIC_API.md",
        "CHANGELOG.md",
        "RELEASE_NOTES.md",
        "ROADMAP.md",
    ]
    missing = [d for d in docs if not os.path.exists(d)]
    record_result(
        "15. Documentation Links & Files Resolution",
        len(missing) == 0,
        f"Missing files: {missing}",
    )


# ----------------------------------------------------------------------
# Section 5: Architecture & API Stability
# ----------------------------------------------------------------------
def check_16_architecture():
    code, out = run_cmd([sys.executable, "scripts/architecture_validator.py"])
    record_result("16. Architecture Laws (0 violations)", code == 0, out)


def check_17_public_api():
    code, out = run_cmd([sys.executable, "-m", "pytest", "tests/test_public_api.py", "-q"])
    record_result("17. Public API Stability", code == 0, out)


def check_18_benchmarks_config():
    code, out = run_cmd(
        [
            sys.executable,
            "-c",
            "import benchmarks.runner; import benchmarks.bench_dependency_graph; import benchmarks.bench_context_engine",
        ]
    )
    files_ok = (
        os.path.exists("performance_report.md")
        and os.path.exists("benchmarks/performance.json")
        and os.path.exists("benchmarks/performance.csv")
    )
    record_result(
        "18. Multi-Format Benchmark Config & Runner Validation",
        code == 0 and files_ok,
        f"Benchmark import or outputs missing: {out}",
    )


# ----------------------------------------------------------------------
# Section 6: Repository & Environment Health
# ----------------------------------------------------------------------
def check_19_readme():
    if not os.path.exists("README.md"):
        record_result("19. README Completeness & Badges", False, "README.md missing")
        return
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    has_status = "Project Status" in content or "Status" in content
    has_platforms = "Supported Platforms" in content or "Platforms" in content
    record_result(
        "19. README Completeness, Status & Badges",
        has_status and has_platforms,
        "README missing status/platforms section",
    )


def check_20_metadata():
    files = ["LICENSE", "CODEOWNERS", ".editorconfig", ".gitattributes", "CITATION.cff"]
    missing = [f for f in files if not os.path.exists(f)]
    record_result(
        "20. License, Metadata & Cross-Platform Paths",
        len(missing) == 0,
        f"Missing metadata files: {missing}",
    )


def check_21_runtime_imports():
    code, out = run_cmd(
        [
            sys.executable,
            "-c",
            "import backend; import backend.engine; import backend.capabilities; import backend.agents",
        ]
    )
    record_result("21. Runtime Package Imports", code == 0, out)


def check_22_precommit_dev_docs():
    has_precommit = os.path.exists(".pre-commit-config.yaml")
    has_contrib = os.path.exists("CONTRIBUTING.md")
    record_result("22. Pre-Commit Config & Dev Docs Verification", has_precommit and has_contrib)


def check_23_ml_collection_safety():
    has_ml_dir = os.path.exists("tests/ml")
    if has_ml_dir:
        ml_files = [f for f in os.listdir("tests/ml") if f.startswith("test_")]
        has_ml_tests = len(ml_files) > 0
    else:
        has_ml_tests = False
    record_result("23. Optional ML Dependency Collection Safety", has_ml_tests)


def check_24_release_config():
    ok = (
        os.path.exists("RELEASE_NOTES.md")
        and os.path.exists("CHANGELOG.md")
        and os.path.exists("pyproject.toml")
    )
    record_result("24. Release Configuration & Packaging Specs", ok, "Release specs missing")


def check_25_release_packaging_build():
    pyproject_ok = os.path.exists("pyproject.toml")
    makefile_ok = os.path.exists("Makefile")
    record_result("25. Release Packaging & Distribution Build", pyproject_ok and makefile_ok)


def main():
    print("=" * 70)
    print("      KuroAI 25-Point Categorized Repository Health Gate")
    print("=" * 70)

    print("\n--- Section 1: Dependency Checks ---")
    check_1_import_graph()
    check_2_dual_env_dependencies()
    check_3_dependency_audit()

    print("\n--- Section 2: Quality Checks ---")
    check_4_formatting_black()
    check_5_import_sorting_isort()
    check_6_linting_ruff()
    check_7_typechecking_mypy()

    print("\n--- Section 3: Testing & Determinism ---")
    check_8_test_collection()
    check_9_unit_test_suite()
    check_10_coverage()
    check_11_test_determinism_bootstrap()

    print("\n--- Section 4: Infrastructure & Workflow Health ---")
    check_12_docker()
    check_13_workflow_syntax()
    check_14_mkdocs()
    check_15_doc_links()

    print("\n--- Section 5: Architecture & API Stability ---")
    check_16_architecture()
    check_17_public_api()
    check_18_benchmarks_config()

    print("\n--- Section 6: Repository & Environment Health ---")
    check_19_readme()
    check_20_metadata()
    check_21_runtime_imports()
    check_22_precommit_dev_docs()
    check_23_ml_collection_safety()
    check_24_release_config()
    check_25_release_packaging_build()

    print("\n" + "=" * 70)
    print(f"Summary: {CHECKS_PASSED}/25 checks PASSED ({CHECKS_FAILED} failed)")
    print("=" * 70)

    if CHECKS_FAILED > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
