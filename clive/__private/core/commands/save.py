from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command
from clive.__private.core.mockcpp import serialize_transaction

if TYPE_CHECKING:
    from pathlib import Path

    from clive.models.transaction import Transaction


class SaveToFile(Command[None]):
    def __init__(self, *, transaction: Transaction, file_path: Path, legacy: bool = False) -> None:
        super().__init__()
        self.__transaction = transaction
        self.__file_path = file_path
        self.__legacy = legacy

    def execute(self) -> None:
        serialized = serialize_transaction(self.__transaction, legacy=self.__legacy)
        with self.__file_path.open("wt", encoding="utf-8") as file:
            file.write(serialized)
