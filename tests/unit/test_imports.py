from __future__ import annotations

import contextlib
import importlib
import sys
import typing
from typing import TYPE_CHECKING

import pytest
from textual import __name__ as textual_package_name

import clive.__private.models.schemas as schemas_models_module
from clive.__private.cli.commands.call_api import get_api_class_name, get_api_client_module_path
from clive.__private.ui import __name__ as ui_package_name
from clive_local_tools.cli.imports import get_cli_help_imports_tree
from clive_local_tools.data.constants import ALL_API_NAMES
from wax import __name__ as wax_package_name

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import ModuleType


def get_tested_api_names() -> list[str]:
    """Get list of api names to be tested for import."""
    invalid_apis = ["search_api"]  # APIs that are not properly generated, fix is already merged in hived
    return [api_name for api_name in ALL_API_NAMES if api_name not in invalid_apis]


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


@pytest.mark.parametrize("api_name", get_tested_api_names())
def test_import_api_package(api_name: str) -> None:
    """Import api package given as argument `api_name`."""
    # ARRANGE
    client_module_name = get_api_client_module_path(api_name)
    api_class_name = get_api_class_name(api_name)

    # ACT & ASSERT
    try:
        importlib.import_module(api_name)
    except Exception as error:  # noqa: BLE001
        pytest.fail(f"API package {api_name} couldn't be imported: {error}")
    try:
        client_module = importlib.import_module(client_module_name)
    except Exception as error:  # noqa: BLE001
        pytest.fail(f"API client module {client_module_name} couldn't be imported: {error}")
    assert hasattr(client_module, api_class_name), (
        f"In api package {api_name} in module {client_module_name} there should be"
        f" definition of api class {api_class_name}"
    )
