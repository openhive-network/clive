from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command
from clive.__private.core.commands.deactivate import Deactivate
from clive.__private.logger import logger

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import timedelta

    from clive.__private.core.app_state import AppState
    from clive.__private.ui.background_tasks import BackgroundTasks


class Activate(Command[bool]):
    def __init__(
        self,
        app_state: AppState,
        background_tasks: BackgroundTasks,
        *,
        active_mode_time: timedelta | None = None,
        auto_deactivate: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(result_default=False)
        self.__app_state = app_state
        self.__background_tasks = background_tasks

        self.__active_mode_time = active_mode_time
        self.__auto_deactivate = auto_deactivate or self.__auto_deactivate_default

    def execute(self) -> None:
        if self.__active_mode_time:
            self.__background_tasks.run_after(self.__active_mode_time, self.__auto_deactivate, name="auto_deactivate")
        self.__app_state.activate()
        logger.info("Mode switched to [bold green]active[/].")
        self._result = True

    def __auto_deactivate_default(self) -> None:
        Deactivate(self.__app_state, self.__background_tasks).execute()
        message = "Mode switched to [bold red]inactive[/] because the active mode time has expired."
        logger.info(message)
