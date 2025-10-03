from __future__ import annotations

import pytest
from textual import __name__ as textual_package_name

import clive.__private.models.schemas as schemas_models_module
from clive.__private.ui import __name__ as ui_package_name
from clive_local_tools.cli.imports import get_cli_help_imports_tree
from wax import __name__ as wax_package_name


@pytest.mark.parametrize(("package_name"), [ui_package_name, textual_package_name, wax_package_name])
def test_not_imported_during_cli_help(package_name: str) -> None:
    # ACT
    cli_imports_tree = get_cli_help_imports_tree()

    # ASSERT
    assert package_name not in cli_imports_tree, f"{package_name} shouldn't be imported during CLI help."


@pytest.mark.parametrize("name", schemas_models_module.__all__)
def test_all_schemas_models_exports_are_importable(name: str) -> None:
    """
    Ensure all names listed in ``__all__`` are actually importable.

    This is especially important because schemas models rely on lazy imports
    (using string-based paths and alias mappings). If an alias is wrong or a module
    path changes, it would break at runtime. This test proactively triggers all
    exports to catch such issues.
    """
    # ACT & ASSERT
    try:
        getattr(schemas_models_module, name)
    except Exception as error:
        raise AssertionError(f"Failed to resolve `{name}` from {schemas_models_module.__name__}") from error
