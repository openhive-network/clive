from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.transfer import Transfer

if TYPE_CHECKING:
    from clive import World


class Commands:
    def __init__(self, world: World) -> None:
        self.__world = world

        self.activate = self.__world.app_state.activate
        self.deactivate = self.__world.app_state.deactivate
        self.transfer = Transfer.execute
