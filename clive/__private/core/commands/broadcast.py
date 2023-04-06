from __future__ import annotations

from clive.__private.core.commands.command import Command
from clive.__private.core.transaction import Transaction
from clive.models.operation import Operation


class Broadcast(Command[bool]):
    """Broadcasts the given operations/transactions to the blockchain."""

    def __init__(self, *content: Operation | Transaction) -> None:
        super().__init__(result_default=False)
        self.__content = content
        self.__transactions = [t for t in content if isinstance(t, Transaction)]

        if transaction := self.__gather_operations_in_transaction():
            self.__transactions.append(transaction)

    def execute(self) -> None:
        for transaction in self.__transactions:
            transaction.broadcast()
        self._result = True

    def __gather_operations_in_transaction(self) -> Transaction | None:
        transaction = Transaction()

        for something in self.__content:
            if isinstance(something, Operation):
                transaction.add(something)

        return transaction if len(transaction) > 0 else None
