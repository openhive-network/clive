from __future__ import annotations

import contextlib
import importlib
import sys
import typing
from typing import TYPE_CHECKING

import pytest
from textual import __name__ as textual_package_name

import clive.__private.models.schemas as schemas_models_module
from clive.__private.ui import __name__ as ui_package_name
from clive_local_tools.cli.imports import get_cli_help_imports_tree
from wax import __name__ as wax_package_name

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import ModuleType


@contextlib.contextmanager
def reload_module_in_type_checking_mode(module_name: str) -> Iterator[ModuleType]:
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(typing, "TYPE_CHECKING", True)
        sys.modules.pop(module_name)
        reloaded = importlib.import_module(module_name)
        try:
            yield reloaded
        finally:
            monkeypatch.setattr(typing, "TYPE_CHECKING", False)
            sys.modules.pop(module_name)
            importlib.import_module(module_name)


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


@pytest.mark.parametrize("name", schemas_models_module.__all__)
def test_schemas_imports_runtime_match_type_checking(name: str) -> None:
    """Ensure all names listed in ``__all__`` point to the same object in runtime and type checking."""
    # ACT
    runtime_object = getattr(schemas_models_module, name)
    with reload_module_in_type_checking_mode(schemas_models_module.__name__) as reloaded:
        typechecking_object = getattr(reloaded, name)

    # ASSERT
    assert runtime_object is typechecking_object, (
        f"Runtime `{runtime_object}` and type checking `{typechecking_object}` objects do not match"
    )
