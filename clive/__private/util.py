from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Generic, TypeVar

from clive.__private.config import ROOT_DIRECTORY, settings
from clive.__private.logger import logger

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import TracebackType


def prepare_before_launch(*, enable_textual_logger: bool = True) -> None:
    def _create_clive_data_directory() -> None:
        Path(settings.DATA_PATH).mkdir(parents=True, exist_ok=True)

    def _copy_settings() -> None:
        user_settings_path = Path(settings.DATA_PATH) / "settings.toml"
        if not user_settings_path.is_file():
            shutil.copy(ROOT_DIRECTORY.parent / "settings.toml", user_settings_path)

    logger.setup(enable_textual=enable_textual_logger)

    _create_clive_data_directory()
    _copy_settings()

    logger.debug(f"settings:\n{settings.as_dict()}")


T = TypeVar("T")


class ExitCallHandler(Generic[T]):
    def __init__(
        self,
        obj: T,
        *,
        exception_callback: Callable[[T, Exception], None] = lambda _, __: None,
        finally_callback: Callable[[T], None] = lambda _: None,
    ) -> None:
        self.__obj = obj
        self.__exception_callback = exception_callback
        self.__finally_callback = finally_callback

    def __enter__(self) -> T:
        return self.__obj

    def __exit__(self, _: type[Exception] | None, ex: Exception | None, ___: TracebackType | None) -> None:
        try:
            if ex is not None:
                self.__exception_callback(self.__obj, ex)
        finally:
            self.__finally_callback(self.__obj)
