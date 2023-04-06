from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command

if TYPE_CHECKING:
    from clive.__private.core.transaction import Transaction
    from clive.__private.storage.mock_database import PrivateKey


class Sign(Command[None]):
    def __init__(self, transaction: Transaction, *, key: PrivateKey) -> None:
        super().__init__()
        self.__transaction = transaction
        self.__key = key

    def execute(self) -> None:
        self.__transaction.sign(self.__key)
