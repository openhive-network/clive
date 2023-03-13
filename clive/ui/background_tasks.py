from __future__ import annotations

import asyncio
from asyncio import Task
from typing import TYPE_CHECKING, Any, Callable

from clive.config import settings

if TYPE_CHECKING:
    from datetime import timedelta

    from clive.ui.app import Clive

TasksDict = dict[str, Task[Any]]


class BackgroundTasks:
    def __init__(self, app: Clive) -> None:
        self.__app = app
        self.__tasks: TasksDict = {}
        self.__delayed_tasks: TasksDict = {}
        self.__long_running_tasks = [
            asyncio.create_task(self.__update_data_from_node()),
            *[asyncio.create_task(self.__debug_log()) if settings.LOG_DEBUG_LOOP else []],
        ]

    @property
    def tasks(self) -> TasksDict:
        return self.__tasks.copy()

    @property
    def delayed_tasks(self) -> TasksDict:
        return self.__delayed_tasks.copy()

    def run(self, name: str, function: Callable[[], Any]) -> None:
        """Create a new background task."""
        self.__tasks[name] = asyncio.create_task(function())

    def run_after(self, time: timedelta, function: Callable[[], Any], name: str | None = None) -> None:
        """Run a function after a given time."""
        name = name or f"run_after_{function.__name__}"

        self.__delayed_tasks[name] = asyncio.create_task(self.__wait_before_call(time, function))

    def cancel(self, name: str) -> None:
        """Cancel a background task."""
        if name in self.__tasks:
            self.__tasks[name].cancel()
        elif name in self.__delayed_tasks:
            self.__delayed_tasks[name].cancel()

    @staticmethod
    async def __wait_before_call(time: timedelta, function: Callable[[], Any]) -> None:
        await asyncio.sleep(time.total_seconds())
        function()

    async def __update_data_from_node(self) -> None:
        while True:
            await asyncio.sleep(3)
            self.__app.log("Updating mock data...")
            self.__app.node_data.recalc()
            self.__app.update_reactive("node_data")

    async def __debug_log(self) -> None:
        while True:
            await asyncio.sleep(1)
            self.__app.log("===================== DEBUG =====================")
            self.__app.log(f"Screen stack: {self.__app.screen_stack}")
            self.__app.log("=================================================")
