from scripts.refactor.update_imports import rewrite_imports

MAPPING = {
    "glpi_dashboard.acl.normalization": "backend.adapters.normalization",
    "glpi_dashboard.acl": "backend.adapters",
}


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
