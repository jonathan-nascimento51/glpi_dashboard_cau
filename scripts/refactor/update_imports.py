import argparse
import json
from pathlib import Path
from typing import Dict

import libcst as cst


def rewrite_imports(code: str, mapping: Dict[str, str]) -> str:
    module = cst.parse_module(code)
    transformer = _ImportTransformer(mapping)
    new_module = module.visit(transformer)
    return new_module.code


class _ImportTransformer(cst.CSTTransformer):
    def __init__(self, mapping: Dict[str, str]) -> None:
        self.mapping = mapping
        self._module = cst.parse_module("")

    def _name_as_str(self, name: cst.BaseExpression) -> str:
        return self._module.code_for_node(name)

    def _update_name(self, name: cst.BaseExpression) -> cst.BaseExpression:
        old = self._name_as_str(name)
        if old in self.mapping:
            return cst.parse_expression(self.mapping[old])
        for key, new in self.mapping.items():
            if old.startswith(key + "."):
                suffix = old[len(key) :]
                return cst.parse_expression(new + suffix)
        return name

    def leave_Import(self, original: cst.Import, updated: cst.Import) -> cst.Import:
        names = []
        changed = False
        for alias in updated.names:
            new_name = self._update_name(alias.name)
            if new_name is not alias.name:
                changed = True
                alias = alias.with_changes(name=new_name)
            names.append(alias)
        return updated.with_changes(names=names) if changed else updated

    def leave_ImportFrom(
        self, original: cst.ImportFrom, updated: cst.ImportFrom
    ) -> cst.ImportFrom:
        if updated.module is None:
            return updated
        new_module = self._update_name(updated.module)
        if new_module is not updated.module:
            return updated.with_changes(module=new_module)
        return updated


def process_paths(paths, mapping: Dict[str, str]) -> None:
    for root in paths:
        for path in Path(root).rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            new_text = rewrite_imports(text, mapping)
            if new_text != text:
                path.write_text(new_text, encoding="utf-8")
                print(f"Updated {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Rewrite imports using file_map.json")
    parser.add_argument(
        "paths", nargs="*", default=["src", "tests"], help="Directories to process"
    )
    parser.add_argument(
        "--map",
        default="scripts/refactor/python_import_map.json",
        help="Path to mapping JSON file",
    )
    args = parser.parse_args()

    mapping = json.loads(Path(args.map).read_text())
    process_paths(args.paths, mapping)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
