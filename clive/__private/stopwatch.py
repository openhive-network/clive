from __future__ import annotations

from time import perf_counter
from typing import TYPE_CHECKING

from clive.__private.logger import logger

if TYPE_CHECKING:
    from types import TracebackType
    from typing import Self


class Stopwatch:
    def __init__(self, name: str) -> None:
        self.__start = self.__now()
        self.__name = name

    def __now(self) -> float:
        return perf_counter()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, _: type[BaseException] | None, ex: BaseException | None, ___: TracebackType | None) -> None:
        logger.debug(f"{self.__name} took: {self.__now() - self.__start:.6f}s")
