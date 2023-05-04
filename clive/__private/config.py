from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Final

from dynaconf import Dynaconf  # type: ignore

ROOT_DIRECTORY: Final[Path] = Path(__file__).parent.parent
TESTS_DIRECTORY: Final[Path] = ROOT_DIRECTORY.parent / "tests"
LAUNCH_TIME: Final[datetime] = datetime.now()
_DATA_DIRECTORY: Final[Path] = Path.home() / ".clive"
_LOG_DIRECTORY: Final[Path] = _DATA_DIRECTORY / "logs"

SETTINGS_FILES: Final[list[str]] = ["settings.toml"]

settings = Dynaconf(
    envvar_prefix="CLIVE",
    root_path=ROOT_DIRECTORY,
    settings_files=SETTINGS_FILES,
    environments=True,
    # preconfigured settings
    data_path=_DATA_DIRECTORY,
    log_path=_LOG_DIRECTORY,
)
