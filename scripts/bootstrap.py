"""
Developer Bootstrap Script for KuroAI.
Automates virtual environment verification, dependency installation, pre-commit hook setup,
and architecture validator execution.

Usage:
    python scripts/bootstrap.py
"""

import os
import subprocess
import sys


def log(msg: str):
    print(f"[BOOTSTRAP] {msg}")


def main():
    log("Starting KuroAI Developer Setup...")

    # 1. Python version check
    log(f"Python Version: {sys.version.split()[0]}")
    if sys.version_info < (3, 10):
        print("[ERROR] Python 3.10+ is required.")
        sys.exit(1)

    # 2. Check virtual environment
    in_venv = sys.prefix != sys.base_prefix
    if not in_venv:
        log(
            "Notice: Not currently running inside a virtual environment. Creating/activating venv recommended."
        )

    # 3. Install developer requirements
    req_dev = os.path.join("requirements", "dev.txt")
    if os.path.exists(req_dev):
        log(f"Installing dependencies from {req_dev}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_dev])
    else:
        log("Warning: requirements/dev.txt not found, installing basic dev dependencies...")
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "pytest",
                "black",
                "ruff",
                "mypy",
                "pre-commit",
            ]
        )

    # 4. Install pre-commit hooks
    log("Installing pre-commit git hooks...")
    try:
        subprocess.check_call([sys.executable, "-m", "pre_commit", "install"])
        log("Pre-commit hooks successfully installed.")
    except Exception as e:
        log(f"Warning: Failed to install pre-commit hooks: {e}")

    # 5. Run Architecture Validator
    log("Running Architecture Validator verification...")
    try:
        subprocess.check_call([sys.executable, "scripts/architecture_validator.py"])
        log("Architecture Validator PASSED (0 violations).")
    except Exception as e:
        print(f"[ERROR] Architecture Validator failed: {e}")
        sys.exit(1)

    log("\n[SUCCESS] Developer Bootstrap Complete! You are ready to contribute to KuroAI.")


if __name__ == "__main__":
    main()
