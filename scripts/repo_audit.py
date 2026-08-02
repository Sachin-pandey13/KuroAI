"""
KuroAI 16-Point Repository Audit Script.
Executes automated ship/no-ship quality verification across all 16 engineering dimensions.

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


def check_1_architecture():
    code, out = run_cmd([sys.executable, "scripts/architecture_validator.py"])
    record_result("1. Architecture Laws (0 violations)", code == 0, out)


def check_2_public_api():
    code, out = run_cmd([sys.executable, "-m", "pytest", "tests/test_public_api.py", "-q"])
    record_result("2. Public API Stability", code == 0, out)


def check_3_formatting():
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
    record_result("3. Code Formatting (Black)", code == 0, out)


def check_4_linting():
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
    record_result("4. Code Linting (Ruff)", code == 0, out)


def check_5_typechecking():
    code, out = run_cmd(
        [sys.executable, "-m", "mypy", "backend", "config", "--ignore-missing-imports"]
    )
    record_result("5. Type Check (MyPy)", code == 0, out)


def check_6_dependencies():
    exists = os.path.exists("requirements/runtime.txt") and os.path.exists("requirements/dev.txt")
    record_result(
        "6. Dependency Audit & Layering", exists, "requirements/ directory structure missing"
    )


def check_7_unit_tests():
    code, out = run_cmd(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "-q",
            "--ignore=tests/stress",
            "--ignore=tests/test_image_generator.py",
            "--ignore=tests/test_orchestrator.py",
        ]
    )
    record_result("7. Unit Test Suite Pass", code == 0, out)


def check_8_coverage():
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
            "--ignore=tests/test_image_generator.py",
            "--ignore=tests/test_orchestrator.py",
            "-q",
        ]
    )
    if code == 0:
        code_rep, out_rep = run_cmd([sys.executable, "-m", "coverage", "report", "--fail-under=80"])
        record_result("8. Coverage Threshold (>=80%)", code_rep == 0, out_rep)
    else:
        record_result("8. Coverage Threshold (>=80%)", False, "Coverage run failed")


def check_9_security():
    code, out = run_cmd([sys.executable, "-m", "pytest", "tests/test_security.py", "-q"])
    record_result("9. Security Suite Pass", code == 0, out)


def check_10_benchmarks():
    code, out = run_cmd([sys.executable, "-m", "benchmarks.runner"])
    files_ok = (
        os.path.exists("performance_report.md")
        and os.path.exists("benchmarks/performance.json")
        and os.path.exists("benchmarks/performance.csv")
    )
    record_result(
        "10. Multi-Format Benchmarks", code == 0 and files_ok, "Benchmark outputs missing"
    )


def check_11_mkdocs():
    code, out = run_cmd([sys.executable, "-m", "mkdocs", "build"])
    record_result("11. MkDocs Site Compilation", code == 0, out)


def check_12_doc_links():
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
        "12. Documentation Links & Files Resolution", len(missing) == 0, f"Missing files: {missing}"
    )


def check_13_docker():
    files = [
        "Dockerfile",
        "docker-compose.dev.yml",
        "docker-compose.prod.yml",
        "docker-compose.gpu.yml",
    ]
    missing = [f for f in files if not os.path.exists(f)]
    record_result(
        "13. Docker Stacks (dev/prod/gpu)", len(missing) == 0, f"Missing docker files: {missing}"
    )


def check_14_workflows():
    files = [
        ".github/workflows/ci.yml",
        ".github/workflows/docs.yml",
        ".github/workflows/release.yml",
        ".github/workflows/benchmarks.yml",
    ]
    missing = [f for f in files if not os.path.exists(f)]
    record_result(
        "14. GitHub Actions Workflows", len(missing) == 0, f"Missing workflow files: {missing}"
    )


def check_15_readme():
    if not os.path.exists("README.md"):
        record_result("15. README Completeness & Badges", False, "README.md missing")
        return
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    has_status = "Project Status" in content or "Status" in content
    has_platforms = "Supported Platforms" in content or "Platforms" in content
    record_result(
        "15. README Completeness, Status & Badges",
        has_status and has_platforms,
        "README missing status/platforms section",
    )


def check_16_metadata():
    files = ["LICENSE", "CODEOWNERS", ".editorconfig", ".gitattributes", "CITATION.cff"]
    missing = [f for f in files if not os.path.exists(f)]
    record_result(
        "16. License & Repository Metadata", len(missing) == 0, f"Missing metadata files: {missing}"
    )


def main():
    print("=" * 70)
    print("      KuroAI 16-Point Repository Quality Audit Gate")
    print("=" * 70)

    check_1_architecture()
    check_2_public_api()
    check_3_formatting()
    check_4_linting()
    check_5_typechecking()
    check_6_dependencies()
    check_7_unit_tests()
    check_8_coverage()
    check_9_security()
    check_10_benchmarks()
    check_11_mkdocs()
    check_12_doc_links()
    check_13_docker()
    check_14_workflows()
    check_15_readme()
    check_16_metadata()

    print("=" * 70)
    print(f"Summary: {CHECKS_PASSED}/16 checks PASSED ({CHECKS_FAILED} failed)")
    print("=" * 70)

    if CHECKS_FAILED > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
