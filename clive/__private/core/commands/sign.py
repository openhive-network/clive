from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command
from clive.__private.core.mockcpp import calculate_digest
from clive.models.transaction import Transaction

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import BeekeeperRemote
    from clive.__private.storage.mock_database import PrivateKeyAlias


class Sign(Command[Transaction]):
    def __init__(self, *, beekeeper: BeekeeperRemote, transaction: Transaction, key: PrivateKeyAlias) -> None:
        super().__init__(result_default=None)
        self.__beekeeper = beekeeper
        self.__transaction = transaction
        self.__key = key

    def execute(self) -> None:
        self.__transaction.transaction_id = calculate_digest(self.__transaction)
        result = self.__beekeeper.api.sign_digest(
            digest=self.__transaction.transaction_id, public_key=self.__key.key_name
        )
        self.__transaction.signatures = [result.signature]
        self._result = self.__transaction
