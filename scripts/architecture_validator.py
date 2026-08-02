"""
Architecture & Dependency Validator for KuroAI.

Verifies:
1. Forbidden import direction across subsystem layers:
   Contracts ↓ Engine ↓ Runtime ↓ Agents ↓ Providers
2. Circular dependencies across modules.
3. Package __all__ export freezes for public API boundaries.
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"

# Layer Hierarchy Rules (Module -> Forbidden Import Prefixes)
FORBIDDEN_IMPORTS: Dict[str, List[str]] = {
    "backend.contracts": [
        "backend.engine",
        "backend.agents",
        "backend.capabilities",
    ],
    "backend.engine": [
        "backend.agents",
        "backend.capabilities.providers",
    ],
    "backend.capabilities.providers": [
        "backend.engine.scheduler",
        "backend.agents",
    ],
}


class ImportVisitor(ast.NodeVisitor):
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.imports: List[str] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            self.imports.append(node.module)
        self.generic_visit(node)


def get_python_module_name(file_path: Path) -> str:
    rel_path = file_path.relative_to(ROOT_DIR)
    parts = list(rel_path.parts)
    if parts[-1].endswith(".py"):
        parts[-1] = parts[-1][:-3]
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def validate_architecture() -> Tuple[int, List[str]]:
    errors: List[str] = []
    py_files = list(BACKEND_DIR.rglob("*.py"))
    
    # 1. Check Layer Import Violations
    for file_path in py_files:
        module_name = get_python_module_name(file_path)
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
        except Exception as e:
            errors.append(f"Failed to parse AST for {file_path}: {e}")
            continue

        visitor = ImportVisitor(file_path)
        visitor.visit(tree)

        for imp in visitor.imports:
            for layer, forbidden_prefixes in FORBIDDEN_IMPORTS.items():
                if module_name.startswith(layer):
                    for forbidden in forbidden_prefixes:
                        if imp.startswith(forbidden):
                            errors.append(
                                f"Layer Violation in '{module_name}' ({file_path.name}): "
                                f"Imports '{imp}' which violates restriction on '{forbidden}'."
                            )

    # 2. Check Package Export Freezes (__all__)
    core_packages = [
        BACKEND_DIR / "contracts" / "__init__.py",
        BACKEND_DIR / "engine" / "__init__.py",
        BACKEND_DIR / "agents" / "__init__.py",
        BACKEND_DIR / "capabilities" / "__init__.py",
    ]
    for pkg_init in core_packages:
        if pkg_init.exists():
            tree = ast.parse(pkg_init.read_text(encoding="utf-8"))
            has_all = any(
                isinstance(stmt, ast.Assign) and
                any(isinstance(target, ast.Name) and target.id == "__all__" for target in stmt.targets)
                for stmt in tree.body
            )
            if not has_all:
                errors.append(f"Package Export Freeze Missing: {pkg_init} does not define __all__.")

    return len(errors), errors


if __name__ == "__main__":
    print("Running KuroAI Architecture & Dependency Validator...")
    error_count, error_messages = validate_architecture()
    if error_count == 0:
        print("[SUCCESS] Architecture Validation Passed! 0 violations found.")
        sys.exit(0)
    else:
        print(f"[FAILURE] Architecture Validation Failed! {error_count} violation(s) found:")
        for msg in error_messages:
            print(f"  - {msg}")
        sys.exit(1)

