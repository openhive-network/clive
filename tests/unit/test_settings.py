from __future__ import annotations

import json
from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.core.constants.env import ENVVAR_PREFIX
from clive.__private.settings._settings import Settings

if TYPE_CHECKING:
    from pathlib import Path

    from clive_local_tools.types import GenericEnvContextFactory


SOME_KEY: Final[str] = "EXAMPLE_KEY"
SOME_VALUE: Final[str] = "EXAMPLE_VALUE"
OVERRIDDEN_VALUE: Final[str] = "OVERRIDDEN"
LOG_LEVELS_KEY: Final[str] = "LOG_LEVELS"
LOG_LEVELS_VALUE_DEFAULT: Final[str] = '["INFO"]'
LOG_LEVELS_VALUE_DEV: Final[str] = '["DEBUG", "INFO"]'
NESTED_GROUP: Final[str] = "NESTED_GROUP"
INNER_KEY: Final[str] = "INNER_KEY"
INNER_VALUE: Final[str] = "INNER_VALUE"
DOTTED_NOTATION_NESTED_KEY = f"{NESTED_GROUP}.{INNER_KEY}"

SETTINGS_FILE_CONTENT: Final[str] = f"""
[default]
{LOG_LEVELS_KEY} = {LOG_LEVELS_VALUE_DEFAULT}
{SOME_KEY} = "{SOME_VALUE}"
[default.{NESTED_GROUP}]
{INNER_KEY} = "{INNER_VALUE}"
[dev]
{LOG_LEVELS_KEY} = {LOG_LEVELS_VALUE_DEV}
"""


@pytest.fixture
def settings_file(tmp_path: Path) -> Path:
    file = tmp_path / "example.toml"
    file.write_text(SETTINGS_FILE_CONTENT.strip())
    return file


@pytest.fixture
def loaded_settings(settings_file: Path) -> Settings:
    return Settings([settings_file])


def test_loading_from_file(settings_file: Path) -> None:
    # ACT
    settings = Settings([settings_file])

    # ASSERT
    assert settings.get(SOME_KEY) == SOME_VALUE, "Value should be loaded from the file."


def test_overridding_with_env_var(
    loaded_settings: Settings, generic_env_context_factory: GenericEnvContextFactory
) -> None:
    # ARRANGE
    env_name = f"{ENVVAR_PREFIX}_{SOME_KEY}"
    env_context_factory = generic_env_context_factory(env_name)

    # ACT
    with env_context_factory(OVERRIDDEN_VALUE):
        # ASSERT
        assert loaded_settings.get(SOME_KEY) == OVERRIDDEN_VALUE, "Value should be overridden by env var."


def test_nested_key_in_file(loaded_settings: Settings) -> None:
    # ACT & ASSERT
    assert loaded_settings.get(DOTTED_NOTATION_NESTED_KEY) == INNER_VALUE, "Value of nested key should be read."


def test_nested_key_in_envvar(loaded_settings: Settings, generic_env_context_factory: GenericEnvContextFactory) -> None:
    # ARRANGE
    inner_value2: Final[str] = INNER_VALUE + "_2"
    env_name = f"{ENVVAR_PREFIX}_{NESTED_GROUP}__{INNER_KEY}"
    env_context_factory = generic_env_context_factory(env_name)

    # ACT
    with env_context_factory(inner_value2):
        # ASSERT
        assert loaded_settings.get(DOTTED_NOTATION_NESTED_KEY) == inner_value2, (
            "Value of nested key should be overridden by env var."
        )


def test_directly_setting_value(loaded_settings: Settings) -> None:
    # ARRANGE
    other_value: Final[str] = "OTHER_VALUE"

    # ACT
    loaded_settings.set(SOME_KEY, other_value)

    # ASSERT
    assert loaded_settings.get(SOME_KEY) == other_value, "Value should overridden by direct setting."


def test_direct_setting_overrides_everything(
    loaded_settings: Settings, generic_env_context_factory: GenericEnvContextFactory
) -> None:
    # ARRANGE
    other_value2: Final[str] = "OTHER_VALUE2"
    env_name = f"{ENVVAR_PREFIX}_{SOME_KEY}"
    env_context_factory = generic_env_context_factory(env_name)

    # ACT
    with env_context_factory(OVERRIDDEN_VALUE):
        loaded_settings.set(SOME_KEY, other_value2)

        # ASSERT
        assert loaded_settings.get(SOME_KEY) == other_value2, "Direct setting should have highest priority."


def test_loading_default_env(settings_file: Path) -> None:
    # ACT
    settings = Settings([settings_file])

    # ASSERT
    log_levels = json.loads(LOG_LEVELS_VALUE_DEFAULT)
    assert settings.get(LOG_LEVELS_KEY) == log_levels, "Environment default should be used."


def test_loading_dev_env(settings_file: Path) -> None:
    # ACT
    settings = Settings([settings_file], env="dev")

    # ASSERT
    log_levels = json.loads(LOG_LEVELS_VALUE_DEV)
    assert settings.get(LOG_LEVELS_KEY) == log_levels, "Environment dev should be used"
