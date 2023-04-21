from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.activate import Activate
from clive.__private.core.commands.broadcast import Broadcast
from clive.__private.core.commands.build_transaction import BuildTransaction
from clive.__private.core.commands.deactivate import Deactivate
from clive.__private.core.commands.fast_broadcast import FastBroadcast
from clive.__private.core.commands.save import SaveToFile
from clive.__private.core.commands.sign import Sign

if TYPE_CHECKING:
    from pathlib import Path

    from clive import World
    from clive.__private.storage.mock_database import PrivateKeyAlias
    from clive.models.operation import Operation
    from clive.models.transaction import Transaction


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

    def sign(self, *, transaction: Transaction, sign_with: PrivateKeyAlias) -> Transaction:
        sign = Sign(beekeeper=self.__world.beekeeper, transaction=transaction, key=sign_with)
        sign.execute()
        return sign.result

    def save_to_file(self, *, transaction: Transaction, path: Path) -> None:
        SaveToFile(transaction=transaction, file_path=path).execute()

    def broadcast(self, *, transaction: Transaction) -> None:
        Broadcast(node_address=self.__world.profile_data.node_address, transaction=transaction).execute()

    def fast_broadcast(self, *, operation: Operation, sign_with: PrivateKeyAlias) -> None:
        FastBroadcast(
            operation=operation,
            beekeeper=self.__world.beekeeper,
            sign_with=sign_with,
            node_address=self.__world.profile_data.node_address,
        ).execute()
