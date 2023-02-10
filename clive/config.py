from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Final

from dynaconf import Dynaconf  # type: ignore

ROOT_DIRECTORY: Final[Path] = Path(__file__).parent
TESTS_DIRECTORY: Final[Path] = ROOT_DIRECTORY.parent / "tests"
LAUNCH_TIME: Final[datetime] = datetime.now()

SETTINGS_FILES: Final[list[str]] = ["settings.toml"]

settings = Dynaconf(
    envvar_prefix="CLIVE",
    root_path=ROOT_DIRECTORY,
    settings_files=SETTINGS_FILES,
    environments=True,
)
