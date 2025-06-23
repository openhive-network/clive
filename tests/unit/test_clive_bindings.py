from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.settings import safe_settings
from clive.__private.ui.bindings import CLIVE_PREDEFINED_BINDINGS, CliveBindings, load_custom_bindings

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from clive.__private.ui.bindings import NestedDictStr


# we use path getter because this code runs before fixtures preparing data_path
@pytest.mark.parametrize(
    "path_getter", [lambda: safe_settings.custom_bindings_path, lambda: safe_settings.default_bindings_path]
)
def test_bindings_path_is_valid(path_getter: Callable[[], Path]) -> None:
    path = path_getter()
    assert path.parent == safe_settings.data_path, "bindings path should be in configured clive data path"


def test_save_and_load() -> None:
    bindings = CliveBindings()
    bindings.dump_toml(safe_settings.custom_bindings_path)
    loaded_bindings = load_custom_bindings()
    assert bindings == loaded_bindings, "Loaded bindings do not match saved bindings"


def test_create_keymap() -> None:
    bindings = CliveBindings()
    keymap = bindings.keymap
    assert len(keymap) > 0, "Keymap should not be empty for default bindings"


def test_override_one_key() -> None:
    new_key = chr(ord(CLIVE_PREDEFINED_BINDINGS.dashboard.operations.key) + 1)
    custom_bindings_dict: NestedDictStr = {"dashboard": {"operations": new_key}}
    bindings = CliveBindings.from_dict(custom_bindings_dict)
    assert CLIVE_PREDEFINED_BINDINGS.dashboard.add_account == bindings.dashboard.add_account, (
        "Key for dashboard.add_account should not change"
    )
    assert CLIVE_PREDEFINED_BINDINGS.dashboard.operations != bindings.dashboard.operations, (
        "Key for dashboard.operations should change"
    )
