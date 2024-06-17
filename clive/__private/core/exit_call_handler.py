from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from types import TracebackType

T = TypeVar("T")


async def dummy(*_: Any) -> None:
    """Fill default values with a dummy callback."""


class ExitCallHandler(Generic[T]):
    def __init__(
        self,
        obj: T,
        *,
        exception_callback: Callable[[T, BaseException], Awaitable[None]] = dummy,
        finally_callback: Callable[[T], Awaitable[None]] = dummy,
    ) -> None:
        self.__obj = obj
        self.__exception_callback = exception_callback
        self.__finally_callback = finally_callback

    async def __aenter__(self) -> T:
        return self.__obj

    async def __aexit__(
        self, _: type[BaseException] | None, ex: BaseException | None, ___: TracebackType | None
    ) -> None:
        try:
            if ex is not None:
                await self.__exception_callback(self.__obj, ex)
        finally:
            await self.__finally_callback(self.__obj)
