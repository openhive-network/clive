from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from clive.__private.core.commands.activate import Activate
from clive.__private.core.commands.broadcast import Broadcast
from clive.__private.core.commands.build_transaction import BuildTransaction
from clive.__private.core.commands.deactivate import Deactivate
from clive.__private.core.commands.fast_broadcast import FastBroadcast
from clive.__private.core.commands.import_key import ImportKey
from clive.__private.core.commands.remove_key import RemoveKey
from clive.__private.core.commands.save_binary import SaveToFileAsBinary
from clive.__private.core.commands.set_timeout import SetTimeout
from clive.__private.core.commands.sign import Sign
from clive.__private.core.commands.sync_data_with_beekeeper import SyncDataWithBeekeeper
from clive.__private.core.commands.update_node_data import UpdateNodeData

if TYPE_CHECKING:
    from pathlib import Path

    from clive import World
    from clive.__private.storage.mock_database import Account, PrivateKey, PublicKey, PublicKeyAliased
    from clive.models import Operation, Transaction


class Commands:
    def __init__(self, world: World) -> None:
        self.__world = world

    def activate(self, *, password: str, time: timedelta | None = None) -> None:
        Activate(
            beekeeper=self.__world.beekeeper, wallet=self.__world.profile_data.name, password=password, time=time
        ).execute()

    def deactivate(self) -> None:
        Deactivate(beekeeper=self.__world.beekeeper, wallet=self.__world.profile_data.name).execute()

    def set_timeout(self, *, seconds: int) -> None:
        SetTimeout(beekeeper=self.__world.beekeeper, seconds=seconds).execute()

    def build_transaction(
        self, *, operations: list[Operation], expiration: timedelta = timedelta(minutes=30)
    ) -> Transaction:
        return BuildTransaction(
            operations=operations, node=self.__world.node, expiration=expiration
        ).execute_with_result()

    def sign(self, *, transaction: Transaction, sign_with: PublicKey) -> Transaction:
        return Sign(
            beekeeper=self.__world.beekeeper,
            transaction=transaction,
            key=sign_with,
            chain_id=self.__world.node.chain_id,
        ).execute_with_result()

    def save_to_file(self, *, transaction: Transaction, path: Path) -> None:
        SaveToFileAsBinary(transaction=transaction, file_path=path).execute()

    def broadcast(self, *, transaction: Transaction) -> None:
        Broadcast(node=self.__world.node, transaction=transaction).execute()

    def fast_broadcast(self, *, operation: Operation, sign_with: PublicKey) -> None:
        FastBroadcast(
            node=self.__world.node,
            operation=operation,
            beekeeper=self.__world.beekeeper,
            sign_with=sign_with,
            chain_id=self.__world.node.chain_id,
        ).execute()

    def import_key(self, *, alias: str, wif: PrivateKey) -> PublicKeyAliased:
        return ImportKey(
            app_state=self.__world.app_state,
            wallet=self.__world.profile_data.name,
            alias=alias,
            key_to_import=wif,
            beekeeper=self.__world.beekeeper,
        ).execute_with_result()

    def remove_key(self, *, password: str, key_to_remove: PublicKey) -> None:
        RemoveKey(
            app_state=self.__world.app_state,
            wallet=self.__world.profile_data.name,
            beekeeper=self.__world.beekeeper,
            key_to_remove=key_to_remove,
            password=password,
        ).execute()

    def sync_data_with_beekeeper(self) -> None:
        SyncDataWithBeekeeper(
            app_state=self.__world.app_state,
            profile_data=self.__world.profile_data,
            beekeeper=self.__world.beekeeper,
        ).execute()

    def update_node_data(self, *, account: Account) -> None:
        UpdateNodeData(account=account, node=self.__world.node).execute()
