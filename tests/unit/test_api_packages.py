from __future__ import annotations

import importlib

import pytest

from clive.__private.cli.commands.call_api import get_api_class_name, get_api_client_module_path
from clive_local_tools.data.constants import ALL_API_NAMES


def get_tested_api_names() -> list[str]:
    """Get list of api names to be tested for import."""
    invalid_apis = ["search_api"]  # APIs that are not properly generated, fix is already merged in hived
    return [api_name for api_name in ALL_API_NAMES if api_name not in invalid_apis]


@pytest.mark.parametrize("api_name", get_tested_api_names())
def test_import_api_package(api_name: str) -> None:
    """Import api package given as argument `api_name`."""
    # ARRANGE
    client_module_name = get_api_client_module_path(api_name)
    api_class_name = get_api_class_name(api_name)

    # ACT & ASSERT
    importlib.import_module(api_name)
    client_module = importlib.import_module(client_module_name)
    assert hasattr(client_module, api_class_name), (
        f"In api package {api_name} in module {client_module_name} there should be"
        f" definition of api class {api_class_name}"
    )
