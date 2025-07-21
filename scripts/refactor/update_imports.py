import argparse
import json
import logging
from pathlib import Path
from typing import Dict, SupportsIndex

import libcst as cst

logging.basicConfig(level=logging.DEBUG)


def rewrite_imports(src: str, mapping: dict[str, str]) -> str:
    return next(
        (src.replace(old, new) for old, new in mapping.items() if old in src),
        src,
    )


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
            if old.startswith(f"{key}."):
                suffix = old[len(key) :]
                return cst.parse_expression(new + suffix)
        return name

    def leave_Import(
        self, original_node: cst.Import, updated_node: cst.Import
    ) -> cst.Import:
        names = []
        changed = False
        for alias in updated_node.names:
            new_name = self._update_name(alias.name)
            if new_name is not alias.name:
                changed = True
                alias = alias.with_changes(name=new_name)
            names.append(alias)
        return updated_node.with_changes(names=names) if changed else updated_node

    def leave_ImportFrom(
        self,
        original_node: cst.ImportFrom,
        updated_node: cst.ImportFrom,
    ) -> cst.ImportFrom:
        if updated_node.module is None:
            return updated_node
        new_module = self._update_name(updated_node.module)
        if new_module is not updated_node.module:
            return updated_node.with_changes(module=new_module)
        return updated_node


def process_paths(paths: list[str], mapping: Dict[str, str]) -> None:
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


MAPPING = {
    "glpi_dashboard.acl.normalization": "backend.adapters.normalization",
    # Adicione outros mapeamentos conforme necessário
}


def test_no_match():
    src = "import some_other_module"
    expected = "import some_other_module"  # Não deve alterar
    assert rewrite_imports(src, MAPPING).strip() == expected


def test_partial_match():
    src = "from glpi_dashboard.acl import something_else"
    expected = "from glpi_dashboard.acl import something_else"  # Não deve alterar
    assert rewrite_imports(src, MAPPING).strip() == expected


def test_import_rewritten():
    src = "import glpi_dashboard.acl.normalization"
    expected = "import backend.adapters.normalization"
    result = rewrite_imports(src, MAPPING).strip()
    logging.debug(f"Reescrevendo: {src} -> {result}")
    assert result == expected


def validate_mapping(mapping: dict[str, str]):
    for key, value in mapping.items():
        assert isinstance(key, str), f"Chave inválida no mapeamento: {key}"
        assert isinstance(value, str), f"Valor inválido no mapeamento: {value}"


validate_mapping(MAPPING)


class Example:
    def append(self, item: SupportsIndex, /) -> None:
        print(f"Appending item: {item}")


example = Example()
example.append(5)  # Works because integers support the __index__ method
