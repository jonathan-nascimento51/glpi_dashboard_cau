from typing import SupportsIndex

from scripts.refactor.update_imports import rewrite_imports

MAPPING = {
    "glpi_dashboard.acl.normalization": "backend.adapters.normalization",
    "glpi_dashboard.acl": "backend.adapters",
}


def validate_mapping(mapping: dict[str, str]):
    for key, value in mapping.items():
        assert isinstance(key, str), f"Chave inválida no mapeamento: {key}"
        assert isinstance(value, str), f"Valor inválido no mapeamento: {value}"


class Example:
    def append(self, item: SupportsIndex, /) -> None:
        print(f"Appending item: {item}")


def test_no_match():
    src = "import some_other_module"
    expected = "import some_other_module"
    assert rewrite_imports(src, MAPPING).strip() == expected


def test_partial_match():
    src = "from glpi_dashboard.acl import something_else"
    expected = "from backend.adapters import something_else"
    assert (
        rewrite_imports(src, MAPPING).strip() == expected
    ), f"Expected '{expected}', but got '{rewrite_imports(src, MAPPING).strip()}'"


def test_validate_mapping():
    validate_mapping(MAPPING)


def test_import_rewritten():
    src = "import glpi_dashboard.acl.normalization"
    expected = "import backend.adapters.normalization"
    assert rewrite_imports(src, MAPPING).strip() == expected


def test_import_as_rewritten():
    src = "import glpi_dashboard.acl.normalization as norm"
    expected = "import backend.adapters.normalization as norm"
    assert rewrite_imports(src, MAPPING).strip() == expected


def test_from_import_rewritten():
    src = "from glpi_dashboard.acl import normalization"
    expected = "from backend.adapters import normalization"
    assert rewrite_imports(src, MAPPING).strip() == expected


def test_from_submodule_import_rewritten():
    src = "from glpi_dashboard.acl.normalization import sanitize_status_column"
    expected = "from backend.adapters.normalization import sanitize_status_column"
    assert rewrite_imports(src, MAPPING).strip() == expected


def test_string_literal_not_rewritten():
    """Verify that string literals containing module names are not rewritten."""
    src = 'variable = "import glpi_dashboard.acl.normalization"'
    assert rewrite_imports(src, MAPPING).strip() == src


def test_multiple_different_imports_rewritten():
    """Verify that multiple different imports in the same file are all rewritten."""
    mapping = {
        "glpi_dashboard.acl": "backend.adapters",
        "some.other.module": "another.new.module",
    }
    src = "import glpi_dashboard.acl\nimport some.other.module"
    expected = "import backend.adapters\nimport another.new.module"
    assert rewrite_imports(src, mapping).strip() == expected
