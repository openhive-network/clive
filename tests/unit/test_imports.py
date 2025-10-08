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


@pytest.mark.parametrize(("package_name"), [ui_package_name, textual_package_name, wax_package_name])
def test_not_imported_during_cli_help(package_name: str) -> None:
    # ACT
    cli_imports_tree = get_cli_help_imports_tree()

    # ASSERT
    assert package_name not in cli_imports_tree, f"{package_name} shouldn't be imported during CLI help."


def test_all_schemas_models_exports_are_importable() -> None:
    """
    Ensure all names listed in ``__all__`` are actually importable.

    This is especially important because schemas models rely on lazy imports
    (using string-based paths and alias mappings). If an alias is wrong or a module
    path changes, it would break at runtime. This test proactively triggers all
    exports to catch such issues.
    """
    # ARRANGE
    module = schemas_models_module

    # ACT
    missing = []

    for name in module.__all__:
        try:
            getattr(module, name)
        except Exception:  # noqa: BLE001
            missing.append(name)

    # ASSERT
    assert not missing, (
        f"The following names from __all__ are missing (failed to resolve) in {module.__name__}: {missing}"
    )


@contextlib.contextmanager
def reload_module_in_type_checking_mode(module_name: str) -> Iterator[ModuleType]:
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(typing, "TYPE_CHECKING", True)
        del sys.modules[module_name]
        reloaded = importlib.reload(importlib.import_module(module_name))
        yield reloaded
        monkeypatch.setattr(typing, "TYPE_CHECKING", False)
        del sys.modules[module_name]
        importlib.reload(importlib.import_module(module_name))


@pytest.mark.parametrize(("name"), schemas_models_module.__all__)
def test_schemas_imports_runtime_match_type_checking(name: str) -> None:
    # ACT
    object_runtime = getattr(schemas_models_module, name)
    with reload_module_in_type_checking_mode(schemas_models_module.__name__) as reloaded:
        object_type = getattr(reloaded, name)

    # ASSERT
    assert object_runtime == object_type, (
        f"Runtime `{object_runtime}` and type checking `{object_type}` objects do not match"
    )
