from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.activate import Activate
from clive.__private.core.commands.build_transaction import BuildTransaction
from clive.__private.core.commands.deactivate import Deactivate

if TYPE_CHECKING:
    from datetime import timedelta

    from clive import World
    from clive.__private.core.transaction import Transaction
    from clive.models.operation import Operation


class Commands:
    def __init__(self, world: World) -> None:
        self.__world = world

    def activate(self, *, password: str) -> None:
        Activate(self.__world.beekeeper, wallet=self.__world.profile_data.name, password=password).execute()

    def deactivate(self) -> None:
        Deactivate(self.__world.beekeeper, wallet=self.__world.profile_data.name).execute()

    def build_transaction(self, *, operations: list[Operation]) -> Transaction:
        bt = BuildTransaction(operations=operations)
        bt.execute()
        return bt.result

    def activate(self, *, active_mode_time: timedelta | None = None) -> None:
        Activate(self.__world.app_state, self.__world.background_tasks, active_mode_time=active_mode_time).execute()

    def deactivate(self) -> None:
        Deactivate(self.__world.app_state, self.__world.background_tasks).execute()
