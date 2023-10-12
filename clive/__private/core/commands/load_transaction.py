from __future__ import annotations

from dataclasses import dataclass
from json import JSONDecodeError
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import CommandError
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.models import Transaction

if TYPE_CHECKING:
    from pathlib import Path


class LoadTransactionError(CommandError):
    pass


@dataclass(kw_only=True)
class LoadTransaction(CommandWithResult[Transaction]):
    file_path: Path

    async def _execute(self) -> None:
        # TODO: should also parse from binary

        try:
            self._result = Transaction.parse_file(self.file_path)
        except JSONDecodeError:
            raise LoadTransactionError(self, f"Failed to parse transaction from file: {self.file_path}") from None
