from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command

if TYPE_CHECKING:
    from pathlib import Path

    from clive.models.transaction import Transaction


@dataclass
class SaveToFileAsJson(Command[None]):
    transaction: Transaction
    file_path: Path

    def execute(self) -> None:
        serialized = self.transaction.as_json()
        with self.file_path.open("wb", encoding="utf-8") as file:
            file.write(serialized)
