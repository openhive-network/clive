from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command
from clive.models.transaction import Transaction

if TYPE_CHECKING:
    from clive.models.operation import Operation


@dataclass
class BuildTransaction(Command[Transaction]):
    operations: list[Operation]

    def execute(self) -> None:
        self._result = Transaction(operations=self.operations)
