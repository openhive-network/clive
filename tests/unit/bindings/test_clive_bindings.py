from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import toml

from clive.__private.settings import safe_settings
from clive.__private.ui.bindings import (
    CLIVE_PREDEFINED_BINDINGS,
    BindingFileInvalidError,
    CliveBindings,
    load_custom_bindings,
)
from clive_local_tools.tui.bindings import copy_custom_bindings, copy_default_bindings, copy_empty_bindings

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from clive.__private.ui.bindings.types import BindingsDict


# we use path getter because this code runs before fixtures preparing data_path
@pytest.mark.parametrize(
    "path_getter", [lambda: safe_settings.custom_bindings_path, lambda: safe_settings.default_bindings_path]
)
def test_bindings_path_is_valid(path_getter: Callable[[], Path]) -> None:
    # ARRANGE
    path = path_getter()

    # ACT & ASSERT
    assert path.parent == safe_settings.data_path, "bindings path should be in configured clive data path"


def test_save_and_load() -> None:
    # ARRANGE
    bindings = CliveBindings()

    # ACT
    bindings.dump_toml(safe_settings.custom_bindings_path)
    loaded_bindings = load_custom_bindings()

    # ASSERT
    assert bindings == loaded_bindings, "Loaded bindings do not match saved bindings"


def test_create_keymap() -> None:
    # ARRANGE
    bindings = CliveBindings()

    # ACT
    keymap = bindings.keymap

    # ASSERT
    assert len(keymap) > 0, "Keymap should not be empty for default bindings"


def test_override_one_key() -> None:
    # ARRANGE
    new_key = chr(ord(CLIVE_PREDEFINED_BINDINGS.dashboard.operations.key) + 1)
    custom_bindings_dict: BindingsDict = {"dashboard": {"operations": new_key}}

    # ACT
    bindings = CliveBindings.from_dict(custom_bindings_dict)

    # ASSERT
    assert CLIVE_PREDEFINED_BINDINGS.dashboard.add_account == bindings.dashboard.add_account, (
        "Key for dashboard.add_account should not change"
    )
    assert CLIVE_PREDEFINED_BINDINGS.dashboard.operations != bindings.dashboard.operations, (
        "Key for dashboard.operations should change"
    )


def test_negative_load_file_with_invalid_toml(tmp_path: Path) -> None:
    # ARRANGE
    file_path = tmp_path / "file1.toml"
    file_path.write_text("<<<   this is invalid toml")

    # ACT & ASSERT
    with pytest.raises(BindingFileInvalidError, match="invalid toml format"):
        CliveBindings.load_toml(file_path)


def test_negative_load_file_with_invalid_ids(tmp_path: Path) -> None:
    # ARRANGE
    file_path = tmp_path / "file1.toml"
    lines = ["[app]", 'invalid_id="g"']
    content = "\n".join(lines)
    file_path.write_text(content)

    # ACT & ASSERT
    with pytest.raises(BindingFileInvalidError, match="Found unknown id"):
        CliveBindings.load_toml(file_path)


def test_negative_load_file_with_invalid_sections(tmp_path: Path) -> None:
    # ARRANGE
    file_path = tmp_path / "file1.toml"
    lines = ["[invalid_section]", 'valid_id="g"']
    content = "\n".join(lines)
    file_path.write_text(content)

    # ACT & ASSERT
    with pytest.raises(BindingFileInvalidError, match="Found unknown section"):
        CliveBindings.load_toml(file_path)


def test_load_custom_bindings() -> None:
    """Test file with custom bindings is loaded properly."""
    # ARRANGE
    file_path = copy_custom_bindings()
    raw_data = toml.load(file_path)

    # ACT
    bindings = CliveBindings.load_toml(file_path)

    # ASSERT
    loaded_data = bindings.to_dict()
    for section_name, raw_value in raw_data.items():
        assert section_name in loaded_data, f"binding section `{section_name}` from file `{raw_data}` has invalid name"
        loaded_value = loaded_data[section_name]
        assert isinstance(raw_value, dict), (
            f"binding section `{section_name}` from file `{raw_data}` should be convertible to dict"
        )
        assert loaded_value.items() >= raw_value.items(), (
            f"loaded bindings in section `{section_name}` with default values should be superset of toml file"
            f" parsed data: `{loaded_value}` raw data in file: `{raw_value}`"
        )


def test_load_empty_bindings() -> None:
    """Test loading empty file give bindings with default values."""
    # ARRANGE
    file_path = copy_empty_bindings()

    # ACT
    bindings = CliveBindings.load_toml(file_path)

    # ASSERT
    assert bindings.to_dict() == CLIVE_PREDEFINED_BINDINGS.to_dict(), "loaded bindings should have only default values"


def test_pattern(tmp_path: Path) -> None:
    """Test default bindings didn't change (use regenerate_default_bindings.py script if changes are expected)."""
    # ARRANGE
    actual_file_path = tmp_path / "file1.toml"
    expected_file_path = copy_default_bindings()

    # ACT
    CLIVE_PREDEFINED_BINDINGS.dump_toml(actual_file_path)

    # ASSERT
    actual = actual_file_path.read_text().split("\n")
    expected = expected_file_path.read_text().split("\n")
    assert actual == expected
