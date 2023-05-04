from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from loguru import logger

from clive.__private.config import settings
from clive.__private.logger import configure_logger

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import TracebackType


def prepare_before_launch() -> None:
    configure_logger()
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
