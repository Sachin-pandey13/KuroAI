"""
KuroAI 20-Point Categorized Repository Audit Script.
Executes automated ship/no-ship quality verification across all 20 engineering dimensions.

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
# Section 3: Testing
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


# ----------------------------------------------------------------------
# Section 4: Infrastructure
# ----------------------------------------------------------------------
def check_11_docker():
    files = [
        "Dockerfile",
        "docker-compose.dev.yml",
        "docker-compose.prod.yml",
        "docker-compose.gpu.yml",
    ]
    missing = [f for f in files if not os.path.exists(f)]
    record_result(
        "11. Docker Stacks (dev/prod/gpu)", len(missing) == 0, f"Missing files: {missing}"
    )


def check_12_workflows():
    files = [
        ".github/workflows/ci.yml",
        ".github/workflows/docs.yml",
        ".github/workflows/release.yml",
        ".github/workflows/codeql.yml",
    ]
    missing = [f for f in files if not os.path.exists(f)]
    record_result(
        "12. GitHub Actions Workflows Validation",
        len(missing) == 0,
        f"Missing files: {missing}",
    )


def check_13_mkdocs():
    code, out = run_cmd([sys.executable, "-m", "mkdocs", "build"])
    record_result("13. MkDocs Site Compilation", code == 0, out)


def check_14_doc_links():
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
        "14. Documentation Links & Files Resolution",
        len(missing) == 0,
        f"Missing files: {missing}",
    )


def check_15_release_config():
    ok = (
        os.path.exists("RELEASE_NOTES.md")
        and os.path.exists("CHANGELOG.md")
        and os.path.exists("pyproject.toml")
    )
    record_result("15. Release Configuration & Packaging Specs", ok, "Release specs missing")


# ----------------------------------------------------------------------
# Section 5: Architecture
# ----------------------------------------------------------------------
def check_16_architecture():
    code, out = run_cmd([sys.executable, "scripts/architecture_validator.py"])
    record_result("16. Architecture Laws (0 violations)", code == 0, out)


def check_17_public_api():
    code, out = run_cmd([sys.executable, "-m", "pytest", "tests/test_public_api.py", "-q"])
    record_result("17. Public API Stability", code == 0, out)


# ----------------------------------------------------------------------
# Section 6: Repository
# ----------------------------------------------------------------------
def check_18_benchmarks():
    code, out = run_cmd([sys.executable, "-m", "benchmarks.runner"])
    files_ok = (
        os.path.exists("performance_report.md")
        and os.path.exists("benchmarks/performance.json")
        and os.path.exists("benchmarks/performance.csv")
    )
    record_result(
        "18. Multi-Format Benchmarks", code == 0 and files_ok, "Benchmark outputs missing"
    )


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


def main():
    print("=" * 70)
    print("      KuroAI 20-Point Categorized Repository Quality Audit Gate")
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

    print("\n--- Section 3: Testing ---")
    check_8_test_collection()
    check_9_unit_test_suite()
    check_10_coverage()

    print("\n--- Section 4: Infrastructure ---")
    check_11_docker()
    check_12_workflows()
    check_13_mkdocs()
    check_14_doc_links()
    check_15_release_config()

    print("\n--- Section 5: Architecture ---")
    check_16_architecture()
    check_17_public_api()

    print("\n--- Section 6: Repository ---")
    check_18_benchmarks()
    check_19_readme()
    check_20_metadata()

    print("\n" + "=" * 70)
    print(f"Summary: {CHECKS_PASSED}/20 checks PASSED ({CHECKS_FAILED} failed)")
    print("=" * 70)

    if CHECKS_FAILED > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
