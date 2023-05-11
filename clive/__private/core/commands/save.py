from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command
from clive.__private.core.iwax import serialize_transaction

if TYPE_CHECKING:
    from pathlib import Path

    from clive.models.transaction import Transaction


@dataclass
class SaveToFile(Command[None]):
    transaction: Transaction
    file_path: Path

    def execute(self) -> None:
        serialized = serialize_transaction(self.transaction)
        with self.file_path.open("wt", encoding="utf-8") as file:
            file.write(serialized)
