from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command
from clive.models.transaction import Transaction

if TYPE_CHECKING:
    from clive.models.operation import Operation


class BuildTransaction(Command[Transaction]):
    def __init__(self, operations: list[Operation]) -> None:
        super().__init__(result_default=None)
        self.__operations = operations

    def execute(self) -> None:
        self._result = Transaction(operations=self.__operations)
