from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command

if TYPE_CHECKING:
    from pathlib import Path

    from clive.models import Transaction


@dataclass(kw_only=True)
class SaveToFileAsJson(Command):
    transaction: Transaction
    file_path: Path

    async def _execute(self) -> None:
        serialized = self.transaction.json(by_alias=True)
        with self.file_path.open("wb", encoding="utf-8") as file:
            file.write(serialized)
