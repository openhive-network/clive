from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.transfer import Transfer
from clive.__private.logger import logger

if TYPE_CHECKING:
    from datetime import timedelta

    from clive import World


class Commands:
    def __init__(self, world: World) -> None:
        self.__world = world

        self.transfer = Transfer.execute

    def activate(self, active_mode_time: timedelta | None = None) -> None:
        logger.info("Mode switched to [bold green]active[/].")

        def __auto_deactivate() -> None:
            self.deactivate()
            message = "Mode switched to [bold red]inactive[/] because the active mode time has expired."
            logger.info(message)

        if active_mode_time:
            self.__world.background_tasks.run_after(active_mode_time, __auto_deactivate, name="auto_deactivate")
        self.__world.app_state.activate()

    def deactivate(self) -> None:
        self.__world.background_tasks.cancel("auto_deactivate")
        self.__world.app_state.deactivate()
