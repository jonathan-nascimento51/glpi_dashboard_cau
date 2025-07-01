"""Static checks for common asyncio anti-patterns."""

from __future__ import annotations

import argparse
import ast
from pathlib import Path


class AsyncAnalyzer(ast.NodeVisitor):
    def __init__(self, filename: Path) -> None:
        self.filename = filename
        self.issues: list[str] = []
        self._async_depth = 0
        self._loop_creations = 0

    # ------------ helper methods ------------
    def visit_Call(self, node: ast.Call) -> None:  # noqa: D401
        """Check function calls for problematic patterns."""
        if isinstance(node.func, ast.Attribute) and isinstance(
            node.func.value, ast.Name
        ):
            base = node.func.value.id
            attr = node.func.attr
            if base == "asyncio" and attr == "new_event_loop":
                self._loop_creations += 1
            if self._async_depth and base == "asyncio" and attr == "run":
                self.issues.append(
                    f"{self.filename}:{node.lineno} asyncio.run dentro de corrotina"
                )
            if self._async_depth and base == "requests":
                self.issues.append(
                    f"{self.filename}:{node.lineno} chamada requests em contexto async"
                )
        if (
            self._async_depth
            and isinstance(node.func, ast.Name)
            and node.func.id == "open"
        ):
            self.issues.append(
                f"{self.filename}:{node.lineno} uso de open() dentro de corrotina"
            )
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: D401
        """Track async function depth."""
        self._async_depth += 1
        self.generic_visit(node)
        self._async_depth -= 1

    def finalize(self) -> None:
        if self._loop_creations > 1:
            self.issues.append(
                f"{self.filename}: multiplas criacoes de event loop "
                f"({self._loop_creations})"
            )


def analyze_file(path: Path) -> list[str]:
    tree = ast.parse(path.read_text())
    analyzer = AsyncAnalyzer(path)
    analyzer.visit(tree)
    analyzer.finalize()
    return analyzer.issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Check asyncio anti-patterns")
    parser.add_argument("path", type=Path, help="File or directory to analyze")
    args = parser.parse_args()

    paths = [args.path]
    if args.path.is_dir():
        paths = list(args.path.rglob("*.py"))

    all_issues: list[str] = []
    for p in paths:
        all_issues.extend(analyze_file(p))

    if all_issues:
        print("Issues detected:")
        for issue in all_issues:
            print(f"- {issue}")
    else:
        print("No issues found.")


if __name__ == "__main__":  # pragma: no cover
    main()
