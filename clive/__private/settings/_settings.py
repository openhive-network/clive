from __future__ import annotations

from pathlib import Path

from dynaconf import Dynaconf  # type: ignore[import-untyped]

from clive.__private.core.constants.env import DATA_DIRECTORY, ENVVAR_PREFIX, ROOT_DIRECTORY, SETTINGS_FILES
from clive.__private.core.constants.setting_identifiers import LOG_DIRECTORY, LOG_PATH

settings = Dynaconf(
    envvar_prefix=ENVVAR_PREFIX,
    root_path=ROOT_DIRECTORY,
    settings_files=SETTINGS_FILES,
    environments=True,
    # preconfigured settings
    data_path=DATA_DIRECTORY,
)

# preconfigured settings, but initialized with a value based on other settings
_log_directory = settings.get(LOG_DIRECTORY, "") or DATA_DIRECTORY
_log_path = Path(_log_directory) / "logs"
settings.set(LOG_PATH, _log_path)


def clive_prefixed_envvar(setting_name: str) -> str:
    underscored_setting_name = setting_name.replace(".", "__")
    return f"{ENVVAR_PREFIX}_{underscored_setting_name}"
