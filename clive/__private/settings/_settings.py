from __future__ import annotations

from pathlib import Path
from typing import Final

from dynaconf import Dynaconf  # type: ignore[import-untyped]

from clive.__private.core.constants.env import ENVVAR_PREFIX, ROOT_DIRECTORY
from clive.__private.core.constants.setting_identifiers import LOG_DIRECTORY, LOG_PATH

_DATA_DIRECTORY: Final[Path] = Path.home() / ".clive"

# order matters - later paths override earlier values for the same key of earlier paths
_SETTINGS_FILES: Final[list[str]] = ["settings.toml", str(_DATA_DIRECTORY / "settings.toml")]

settings = Dynaconf(
    envvar_prefix=ENVVAR_PREFIX,
    root_path=ROOT_DIRECTORY,
    settings_files=_SETTINGS_FILES,
    environments=True,
    # preconfigured settings
    data_path=_DATA_DIRECTORY,
)

# preconfigured settings, but initialized with a value based on other settings
_log_directory = settings.get(LOG_DIRECTORY, "") or _DATA_DIRECTORY
_log_path = Path(_log_directory) / "logs"
settings.set(LOG_PATH, _log_path)
