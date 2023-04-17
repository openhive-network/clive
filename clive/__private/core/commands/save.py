from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.transaction import Transaction


class SaveToFile(Command[None]):
    def __init__(self, transaction: Transaction, file_path: Path) -> None:
        super().__init__()
        self.__transaction = transaction
        self.__file_path = file_path

    def execute(self) -> None:
        self.__transaction.save_to_file(self.__file_path)
