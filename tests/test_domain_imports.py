import ast
import importlib
import importlib.util
import pkgutil


def iter_domain_modules():
    package = importlib.import_module("backend.domain")
    yield package.__name__
    for modinfo in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        yield modinfo.name


def get_imported_modules(module_name: str) -> list[str]:
    spec = importlib.util.find_spec(module_name)
    if not spec or not spec.origin:
        return []
    with open(spec.origin, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=spec.origin)
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module = "." * node.level + node.module if node.level else node.module
                imports.append(module)
    return imports


def test_domain_has_no_dependency_on_outer_layers():
    disallowed_prefixes = ("backend.application", "backend.infrastructure")
    for module_name in iter_domain_modules():
        for imported in get_imported_modules(module_name):
            for prefix in disallowed_prefixes:
                assert not imported.startswith(
                    prefix
                ), f"{module_name} imports {imported}"
