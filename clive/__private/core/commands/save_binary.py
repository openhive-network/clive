from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.iwax import serialize_transaction

if TYPE_CHECKING:
    from pathlib import Path

    from clive.models import Transaction


@dataclass(kw_only=True)
class SaveToFileAsBinary(Command):
    transaction: Transaction
    file_path: Path

    def _execute(self) -> None:
        serialized = serialize_transaction(self.transaction)
        with self.file_path.open("wb", encoding="utf-8") as file:
            file.write(serialized)
