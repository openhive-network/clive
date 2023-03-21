from __future__ import annotations

import asyncio
from asyncio import Task
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Callable

from textual.message import Message

from clive.config import settings
from clive.core.callback import invoke
from clive.core.communication import Communication

if TYPE_CHECKING:
    from clive.ui.app import Clive

TasksDict = dict[str, Task[Any]]


class BackgroundErrorOccurred(Message):
    def __init__(self, exception: Exception) -> None:
        self.exception = exception
        super().__init__()


class BackgroundTasks:
    def __init__(self, app: Clive) -> None:
        self.__app = app
        self.__tasks: TasksDict = {}

        self.run_every(timedelta(seconds=3), self.__update_data_from_node)
        if settings.LOG_DEBUG_LOOP:
            self.run_every(timedelta(seconds=1), self.__debug_log)

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
            await self.__wait_before_call(time, function)
            await __loop()

        name = name or f"continuous-{function.__name__}"
        self.__tasks[name] = asyncio.create_task(__loop())

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
            self.__app.post_message(BackgroundErrorOccurred(error))

    def __update_data_from_node(self) -> None:
        self.__app.log("Updating mock data...")
        self.__app.node_data.recalc()
        self.__app.update_reactive("node_data")

    async def __debug_log(self) -> None:
        self.__app.log("===================== DEBUG =====================")

        self.__app.log(f"Screen stack: {self.__app.screen_stack}")
        self.__app.log(f"Background tasks: { {name: task._state for name, task in self.__tasks.items()} }")

        query = {"jsonrpc": "2.0", "method": "database_api.get_dynamic_global_properties", "id": 1}
        response = await Communication.request(str(self.__app.profile_data.node_address), data=query)
        result = response.json()
        self.__app.log(f'Current block: {result["result"]["head_block_number"]}')

        self.__app.log("=================================================")
