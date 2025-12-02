from __future__ import annotations

import importlib

import pytest

from clive.__private.cli.commands.call import (
    get_api_class_name,
    get_api_client_module_path,
    get_api_description_module_path,
)
from clive_local_tools.data.constants import API_NAMES


@pytest.mark.parametrize("api_name", API_NAMES)
def test_import_api_package(api_name: str) -> None:
    """Import api package given as argument `api_name`."""
    # ARRANGE
    description_module_name = get_api_description_module_path(api_name)
    client_module_name = get_api_client_module_path(api_name)
    api_class_name = get_api_class_name(api_name)

    # ACT & ASSERT
    importlib.import_module(api_name)
    importlib.import_module(description_module_name)
    client_module = importlib.import_module(client_module_name)
    assert hasattr(client_module, api_class_name), (
        f"In api package {api_name} in module {client_module_name} there should be"
        f" definition of api class {api_class_name}"
    )
