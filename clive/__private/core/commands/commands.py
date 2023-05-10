from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.activate import Activate
from clive.__private.core.commands.broadcast import Broadcast
from clive.__private.core.commands.build_transaction import BuildTransaction
from clive.__private.core.commands.deactivate import Deactivate
from clive.__private.core.commands.fast_broadcast import FastBroadcast
from clive.__private.core.commands.import_key import ImportKey
from clive.__private.core.commands.save_binary import SaveToFileAsBinary
from clive.__private.core.commands.set_timeout import SetTimeout
from clive.__private.core.commands.sign import Sign

if TYPE_CHECKING:
    from datetime import timedelta
    from pathlib import Path

    from clive import World
    from clive.__private.storage.mock_database import PrivateKey, PrivateKeyAlias
    from clive.models.operation import Operation
    from clive.models.transaction import Transaction


class Commands:
    def __init__(self, world: World) -> None:
        self.__world = world

    def activate(self, *, password: str, time: timedelta | None = None) -> None:
        Activate(self.__world.beekeeper, wallet=self.__world.profile_data.name, password=password, time=time).execute()

    def deactivate(self) -> None:
        Deactivate(self.__world.beekeeper, wallet=self.__world.profile_data.name).execute()

    def set_timeout(self, *, seconds: int) -> None:
        SetTimeout(beekeeper=self.__world.beekeeper, seconds=seconds).execute()

    def build_transaction(self, *, operations: list[Operation]) -> Transaction:
        return BuildTransaction(operations=operations).execute_with_result()

    def sign(self, *, transaction: Transaction, sign_with: PrivateKeyAlias) -> Transaction:
        return Sign(
            beekeeper=self.__world.beekeeper,
            transaction=transaction,
            key=sign_with,
            chain_id=self.__world.profile_data.chain_id,
        ).execute_with_result()

    def save_to_file(self, *, transaction: Transaction, path: Path) -> None:
        SaveToFileAsBinary(transaction=transaction, file_path=path).execute()

    def broadcast(self, *, transaction: Transaction) -> None:
        Broadcast(node=self.__world.node, transaction=transaction).execute()

    def fast_broadcast(self, *, operation: Operation, sign_with: PrivateKeyAlias) -> None:
        FastBroadcast(
            node=self.__world.node,
            operation=operation,
            beekeeper=self.__world.beekeeper,
            sign_with=sign_with,
            chain_id=self.__world.profile_data.chain_id,
        ).execute()

    def import_key(self, *, wif: PrivateKey) -> PrivateKeyAlias:
        return ImportKey(
            wallet=self.__world.profile_data.name, key_to_import=wif, beekeeper=self.__world.beekeeper
        ).execute_with_result()
