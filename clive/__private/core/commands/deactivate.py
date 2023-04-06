from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command

if TYPE_CHECKING:
    from clive.__private.core.app_state import AppState
    from clive.__private.ui.background_tasks import BackgroundTasks


class Deactivate(Command[bool]):
    def __init__(self, app_state: AppState, background_tasks: BackgroundTasks) -> None:
        super().__init__(result_default=False)
        self.__app_state = app_state
        self.__background_tasks = background_tasks

    def execute(self) -> None:
        self.__background_tasks.cancel("auto_deactivate")
        self.__app_state.deactivate()
        self._result = True
