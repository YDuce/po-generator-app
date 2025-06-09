import ast
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1] / "app"


def _check(path: Path, module: str) -> bool:
    if path.parts[1] == "api" and module.startswith("app.channels"):
        return False
    if (
        path.parts[1] == "core"
        and module.startswith("app.")
        and not module.startswith("app.core")
    ):
        return False
    if path.parts[1] == "channels" and module.startswith("app.api"):
        return False
    return True


def test_import_graph():
    violations = []
    for py in APP_ROOT.rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if not _check(py, node.module):
                    violations.append(f"{py} -> {node.module}")
    assert not violations, "Forbidden imports found: " + ", ".join(violations)
