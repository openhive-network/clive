from __future__ import annotations

import copy
import os
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

import toml

from clive.__private.core.constants.env import ENVVAR_PREFIX, ROOT_DIRECTORY
from clive.__private.core.constants.setting_identifiers import LOG_DIRECTORY, LOG_PATH

if TYPE_CHECKING:
    from collections.abc import Sequence

_DATA_DIRECTORY: Final[Path] = Path.home() / ".clive"

# order matters - later paths override earlier values for the same key of earlier paths
_SETTINGS_FILES: Final[list[Path]] = [ROOT_DIRECTORY / "settings.toml", _DATA_DIRECTORY / "settings.toml"]

type KeyDottedNotation = str
"""A string representing a key in dotted notation format (e.g., 'NODE.CHAIN_ID')."""

type EnvName = str
"""The name of the environment"""

type EnvSettings = dict[str, Any]
"""A mapping representing environment settings (which may be nested)."""

type EnvNameToEnvSettings = dict[str, EnvSettings]
"""A mapping between environment name and environment settings (which may be nested)."""


class Settings:
    """
    A configuration settings manager for handling environment-specific settings.

    This class allows loading configuration from various sources such as files, environmental
    variables, and programmatically set values. It supports managing environment-specific settings
    with a precedence of overrides, environment variables, file-based values, and defaults.

    Example:
        Assuming no default is provided via init (which has the lowest priority):

        When the settings file contains
        ```toml
        [FIRST_GROUP.NESTED_GROUP]
        SOME_KEY = 123
        ```

        The environment variable
        ```bash
        CLIVE__FIRST_GROUP__NESTED_GROUP__SOME_KEY=124
        ```
        would override the setting in the file.

        The KeyDottedNotation for this setting is "FIRST_GROUP.NESTED_GROUP.SOME_KEY".

        Alternatively, calling
        ```python
        settings.set("FIRST_GROUP.NESTED_GROUP.SOME_KEY", 125)
        ```
        will take the highest precedence.

    Attributes:
        DEFAULT_ENV_NAME: The default environment name.

    Args:
        files: Sequence of file paths containing settings.
        prefix: String prefix for environment variables (must be alphabetic).
        env: Name of the initial environment to use.
        **defaults: Additional default values to use as base settings.
    """

    DEFAULT_ENV_NAME: Final[str] = "DEFAULT"

    def __init__(
        self,
        files: Sequence[str | Path],
        prefix: str = ENVVAR_PREFIX,
        env: str = DEFAULT_ENV_NAME,
        **defaults: Any,
    ) -> None:
        assert prefix.isalpha(), "Prefix should be an alphabetic string"

        self._files = [Path(f) for f in files]
        self._prefix = prefix
        self._env = self._normalize_key(env)
        self._defaults: EnvSettings = self._normalize_keys(defaults)
        self._data: EnvNameToEnvSettings = {}
        self._overrides: EnvNameToEnvSettings = {}
        self.reload()

    @property
    def env(self) -> EnvName:
        """
        Get the currently active environment name.

        Returns:
            Environment name.
        """
        return self._env

    def setenv(self, env: EnvName) -> None:
        """
        Change the active environment.

        Args:
            env: Name of the environment to switch to (e.g., "dev", "default").
        """
        self._env = self._normalize_key(env)

    def get(
        self,
        key: KeyDottedNotation,
        default: object | None = None,
    ) -> object | None:
        """
        Get a setting by key.

        Args:
            key: Key of the setting to get. Use dot notation for nested values.
            default: Default value to return if the key does not exist.

        Returns:
            Value of the setting if found or `default`.
        """
        merged = self._resolve()
        value = self._resolve_from_dict(merged, key)
        return value if value is not None else default

    def set(
        self,
        key: KeyDottedNotation,
        value: object | None,
        env: str | None = None,
    ) -> None:
        """
        Set a setting with a key in the active env (or given env) to a given value.

        Args:
            key: Key of the setting to set. Use dot notation for nested values.
            value: Value of the setting to set.
            env: Environment to which the setting is to be set.
        """
        target_env_name = self._normalize_key(env or self.env)
        overrides_env = self._overrides.setdefault(target_env_name, {})
        self._set_nested(overrides_env, key, value)

    def reload(self) -> None:
        """Clear the current state and reload from files."""
        self._data.clear()
        self._data[self.DEFAULT_ENV_NAME] = copy.deepcopy(self._defaults)
        for file in self._files:
            self._load_file(file)

    def as_dict(self, env: EnvName | None = None) -> EnvSettings:
        """
        Get a dictionary representation of the current settings.

        Args:
            env: Environment to which the settings are to be reloaded from. Default to active.

        Returns:
            Dictionary representation of the settings.
        """
        return self._resolve(env)

    def _resolve(self, env: EnvName | None = None) -> EnvSettings:
        """
        Resolve the current environment settings with the correct order.

        The priority order is:
            1. Dynamic overrides
            2. Environment variables
            3. File-based settings
            4. Defaults (given during init)

        Args:
            env: Environment to which the settings are to be resolved.

        Returns:
            Resolved environment settings.
        """
        env = self._normalize_key(env or self.env)

        # 1. Start with defaults
        merged = copy.deepcopy(self._data.get(self.DEFAULT_ENV_NAME, {}))

        # 2. Merge TOML values for environment
        if env != self.DEFAULT_ENV_NAME:
            env_data = self._data.get(env, {})
            self._merge(merged, copy.deepcopy(env_data))

        # 3. Apply environment variables
        self._merge(merged, self._parse_prefixed_envvars())

        # 4. Apply dynamic overrides (they should overwrite everything)
        overrides = self._overrides.get(env, {})
        self._merge(merged, copy.deepcopy(overrides))

        return merged

    @property
    def _full_prefix(self) -> str:
        return f"{self._prefix}_"

    def _set_nested(
        self,
        target: dict[str, Any],
        dotted_key: KeyDottedNotation,
        value: object | None,
    ) -> None:
        """
        Set a value in a target dictionary using dotted notation.

        Args:
            target: Target mapping to set the value to.
            dotted_key:  Key in dotted notation format.
            value: Value to set.
        """
        parts = self._dotted_key_notation_to_parts(dotted_key)
        node = target
        for part in parts[:-1]:
            node = node.setdefault(self._normalize_key(part), {})
        node[self._normalize_key(parts[-1])] = value

    def _load_file(self, filepath: Path) -> None:
        """
        Load settings from a given TOML file.

        Args:
            filepath: Path to the TOML file.
        """
        if not filepath.exists():
            return

        content = toml.loads(filepath.read_text())

        for env_name_raw, env_data_raw in content.items():
            env_name_normalized = self._normalize_key(env_name_raw)
            env_data_normalized = self._normalize_keys(env_data_raw)
            current_env_data = self._data.setdefault(env_name_normalized, {})
            self._merge(current_env_data, env_data_normalized)

    def _merge(self, target: dict[str, Any], new_data: dict[str, Any]) -> None:
        """
        Merges the content of one dictionary into another.

        Args:
            target: The main dictionary that will be updated with the new data.
            new_data: The dictionary containing new key-value pairs to merge into the target.

        Example:
            >>> dict1 = {"a": {"x": 1}}
            >>> dict2 = {"a": {"y": 2}}
            >>> _merge(dict1, dict2)
            >>> dict1
            {'a': {'x': 1, 'y': 2}}
        """
        for key, value in new_data.items():
            if isinstance(value, dict):
                node = target.setdefault(key, {})
                self._merge(node, value)
            else:
                target[key] = value

    def _resolve_from_dict(self, data: EnvSettings, dotted_key: KeyDottedNotation) -> object | None:
        """
        Resolves a value from a nested dictionary using a dotted key notation.

        Args:
            data: The dictionary to resolve the value from.
            dotted_key: The dotted key notation representing the desired path.

        Returns:
            The resolved value from the dictionary or None if the path cannot
            be resolved.
        """
        parts = self._dotted_key_notation_to_parts(dotted_key)
        node: object | None = data
        for part in parts:
            if not isinstance(node, dict):
                return None
            node = node.get(self._normalize_key(part))
            if node is None:
                return None
        return node

    def _parse_prefixed_envvars(self) -> dict[str, Any]:
        result: dict[str, Any] = {}

        for env_key, env_value in os.environ.items():
            if not env_key.startswith(self._full_prefix):
                continue

            dotted_key = self._envvar_to_dotted_key_notation(env_key, self._full_prefix)
            self._set_nested(result, dotted_key, env_value)

        return result

    def _dotted_key_notation_to_parts(self, dotted_key: str) -> list[str]:
        """
        Converts a dotted key notation string into a list of its parts.

        Args:
            dotted_key: Key in dotted notation format.

        Returns:
            Parts of the original dotted key.
        """
        return [self._normalize_key(part) for part in dotted_key.split(".")]

    def _envvar_to_dotted_key_notation(self, env_key: str, prefix: str) -> str:
        """
        Converts an environment variable key with a given prefix to a dotted key notation.

        Args:
            env_key: Environment variable name.
            prefix: Environment variable prefix.

        Returns:
            Dotted key notation of the environment variable.
        """
        normalized = self._normalize_key(env_key)
        stripped = normalized[len(prefix) :]
        parts = stripped.split("__")
        return ".".join(parts)

    def _normalize_key(self, key: str) -> str:
        return key.upper()

    def _normalize_keys(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Recursively normalize all dictionary keys.

        Args:
            data: A dictionary whose keys will be normalized.

        Returns:
            A new dictionary with normalized keys.
        """
        normalized: dict[str, Any] = {}
        for key, value in data.items():
            new_key = self._normalize_key(key)
            if isinstance(value, dict):
                normalized[new_key] = self._normalize_keys(value)
            else:
                normalized[new_key] = value
        return normalized


@cache
def get_settings() -> Settings:
    settings = Settings(
        files=_SETTINGS_FILES,
        data_path=_DATA_DIRECTORY,
    )

    # preconfigured settings, but initialized with a value based on other settings
    _log_directory = settings.get(LOG_DIRECTORY, "") or _DATA_DIRECTORY
    _log_path = Path(_log_directory) / "logs"
    settings.set(LOG_PATH, _log_path)
    return settings
