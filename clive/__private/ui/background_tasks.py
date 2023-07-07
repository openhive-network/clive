from __future__ import annotations

import asyncio
from asyncio import Task
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from textual.message import Message

from clive.__private.core._thread import thread_pool
from clive.__private.core.callback import invoke
from clive.__private.logger import logger

if TYPE_CHECKING:
    from datetime import timedelta


TasksDict = dict[str, Task[Any]]
ErrorCallbackT = Callable[[Exception], None]
ThreadPoolClosedCallbackT = Callable[[], bool]


class BackgroundErrorOccurred(Message):
    def __init__(self, exception: Exception) -> None:
        self.exception = exception
        super().__init__()


class BackgroundTasks:
    def __init__(self, *, exception_handler: ErrorCallbackT | None = None) -> None:
        self.__exception_handler = exception_handler
        self.__thread_pool = thread_pool
        self.__tasks: TasksDict = {}

    @property
    def tasks(self) -> TasksDict:
        return self.__tasks.copy()

    def run(self, function: Callable[[], Any], *, name: str | None = None) -> None:
        """Create a new background task."""
        name = name or function.__name__
        self.__tasks[name] = asyncio.create_task(self.__run_safely(function))

    def run_after(self, time: timedelta, function: Callable[[], Any], *, name: str | None = None) -> None:
        """Run a function after a given time."""
        name = name or f"delayed-{function.__name__}"
        self.__tasks[name] = asyncio.create_task(self.__wait_before_call(time, function))

    def run_every(self, time: timedelta, function: Callable[[], Any], *, name: str | None = None) -> None:
        """Run a function every given time."""

        async def __loop() -> None:
            while True:
                await self.__wait_before_call(time, function)

        name = name or f"continuous-{function.__name__}"
        self.__tasks[name] = asyncio.create_task(__loop())

    def run_in_thread(self, function: Callable[[ThreadPoolClosedCallbackT], None]) -> None:
        self.__thread_pool.submit(function, lambda: self.__thread_pool._shutdown)

    def cancel(self, name: str, *, remove: bool = True) -> None:
        """Cancel a background task."""
        if name in self.__tasks:
            self.__tasks[name].cancel()

        if remove:
            self.__tasks.pop(name, None)

    async def __wait_before_call(self, time: timedelta, function: Callable[[], Any]) -> None:
        await asyncio.sleep(time.total_seconds())
        await self.__run_safely(function)

    async def __run_safely(self, function: Callable[[], Any]) -> None:
        try:
            await invoke(function)
        except Exception as error:  # noqa: BLE001
            if self.__exception_handler:
                self.__exception_handler(error)
            else:
                logger.error(f"Unhandled exception in background tasks: {error}")
