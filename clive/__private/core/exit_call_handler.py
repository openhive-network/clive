from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import TracebackType

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
