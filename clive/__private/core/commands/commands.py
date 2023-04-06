from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.activate import Activate
from clive.__private.core.commands.deactivate import Deactivate
from clive.__private.core.commands.transfer import Transfer

if TYPE_CHECKING:
    from datetime import timedelta

    from clive import World


class Commands:
    def __init__(self, world: World) -> None:
        self.__world = world

        self.transfer = Transfer

    def activate(self, *, active_mode_time: timedelta | None = None) -> None:
        Activate(self.__world.app_state, self.__world.background_tasks, active_mode_time=active_mode_time).execute()

    def deactivate(self) -> None:
        Deactivate(self.__world.app_state, self.__world.background_tasks).execute()
