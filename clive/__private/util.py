from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Generic, TypeVar

from loguru import logger

from clive.__private.config import ROOT_DIRECTORY, settings
from clive.__private.logger import configure_logger

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import TracebackType


def prepare_before_launch() -> None:
    def _create_clive_data_directory() -> None:
        Path(settings.DATA_PATH).mkdir(parents=True, exist_ok=True)

    def _copy_settings() -> None:
        user_settings_path = Path(settings.DATA_PATH) / "settings.toml"
        if not user_settings_path.is_file():
            shutil.copy(ROOT_DIRECTORY.parent / "settings.toml", user_settings_path)

    configure_logger()

    _create_clive_data_directory()
    _copy_settings()

    logger.debug(f"settings:\n{settings.as_dict()}")


T = TypeVar("T")


class ExitCallHandler(Generic[T]):
    def __init__(self, obj: T, exit_callback: Callable[[T], None]) -> None:
        self.__obj = obj
        self.__exit_callback = exit_callback

    def __enter__(self) -> T:
        return self.__obj

    def __exit__(self, _: type[Exception] | None, __: Exception | None, ___: TracebackType | None) -> None:
        self.__exit_callback(self.__obj)
