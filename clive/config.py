from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Final

from dynaconf import Dynaconf  # type: ignore
from dynaconf.loaders.toml_loader import write  # type: ignore
from prompt_toolkit.keys import Keys

from clive.exceptions import KeyBindingException

ROOT_DIRECTORY: Final[Path] = Path(__file__).parent
TESTS_DIRECTORY: Final[Path] = ROOT_DIRECTORY.parent / "tests"
LAUNCH_TIME: Final[datetime] = datetime.now()

SETTINGS_FILES: Final[list[str]] = ["settings.toml", "style.toml"]

settings = Dynaconf(
    envvar_prefix="CLIVE",
    root_path=ROOT_DIRECTORY,
    settings_files=SETTINGS_FILES,
    environments=True,
)


def update(settings_file: str, data: dict[str, Any], *, merge: bool = True) -> None:
    if settings_file not in SETTINGS_FILES:
        raise ValueError(f"settings_file must be one of {SETTINGS_FILES}")

    write(ROOT_DIRECTORY.parent / settings_file, data, merge)


def get_bind_from_config(name: str) -> Keys:
    binding = settings.key_bindings.get(name)
    if not binding:
        raise KeyBindingException(f"Key binding `{name}` was not found in the settings.toml file")

    try:
        return Keys(binding)
    except ValueError as exception:
        raise KeyBindingException(f"Invalid key binding: {binding}.") from exception
