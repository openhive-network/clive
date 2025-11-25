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
from clive_local_tools.data.constants import API_NAMES

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import ModuleType


@pytest.mark.parametrize("api_name", API_NAMES)
def test_import_api_package(api_name: str) -> None:
    """Import api package given as argument `api_name`."""
    # ACT & ASSERT
    importlib.import_module(api_name)
