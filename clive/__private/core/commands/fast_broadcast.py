from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command
from clive.__private.core.perform_actions_on_transaction import perform_actions_on_transaction

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import BeekeeperRemote
    from clive.__private.storage.mock_database import NodeAddress, PrivateKeyAlias
    from clive.models.operation import Operation


class FastBroadcast(Command[None]):
    def __init__(
        self, *, operation: Operation, beekeeper: BeekeeperRemote, sign_with: PrivateKeyAlias, address: NodeAddress
    ) -> None:
        super().__init__()
        self.__operation = operation
        self.__sign_with = sign_with
        self.__node_address = address
        self.__beekeeper = beekeeper

    def execute(self) -> None:
        perform_actions_on_transaction(
            content=self.__operation,
            beekeeper=self.__beekeeper,
            node_address=self.__node_address,
            sign_key=self.__sign_with,
            save_file_path=None,
            broadcast=True,
        )
