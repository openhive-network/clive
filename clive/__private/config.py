from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Final

from dynaconf import Dynaconf  # type: ignore[import-untyped]

ROOT_DIRECTORY: Final[Path] = Path(__file__).parent.parent
TESTS_DIRECTORY: Final[Path] = ROOT_DIRECTORY.parent / "tests"
LAUNCH_TIME: Final[datetime] = datetime.now()  # noqa: DTZ005; we want to use the local timezone
_DATA_DIRECTORY: Final[Path] = Path.home() / ".clive"

# order matters - later paths override earlier values for the same key of earlier paths
SETTINGS_FILES: Final[list[str]] = ["settings.toml", str(_DATA_DIRECTORY / "settings.toml")]

settings = Dynaconf(
    envvar_prefix="CLIVE",
    root_path=ROOT_DIRECTORY,
    settings_files=SETTINGS_FILES,
    environments=True,
    # preconfigured settings
    data_path=_DATA_DIRECTORY,
)

log_directory = settings.get("LOG_DIRECTORY", "") or _DATA_DIRECTORY
log_path = Path(log_directory) / "logs"
settings.set("LOG_PATH", log_path)
