from __future__ import annotations

import contextlib
from dataclasses import dataclass
from json import JSONDecodeError
from typing import TYPE_CHECKING

from clive.__private.core import iwax
from clive.__private.core.commands.abc.command import CommandError
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.iwax import WaxOperationFailedError
from clive.__private.models.transaction import Transaction

if TYPE_CHECKING:
    from pathlib import Path


class LoadTransactionError(CommandError):
    pass


@dataclass(kw_only=True)
class LoadTransaction(CommandWithResult[Transaction]):
    file_path: Path

    async def _execute(self) -> None:
        # Models are built without validation, so only content which is not JSON (e.g. binary form - a hex string,
        # not UTF-8 text) or JSON which is not an object (`TypeError` when building the model) is rejected here.
        with contextlib.suppress(JSONDecodeError, UnicodeDecodeError, TypeError):
            self._result = Transaction.parse_raw(self.file_path.read_text())
            return

        with contextlib.suppress(WaxOperationFailedError, UnicodeDecodeError, JSONDecodeError):
            self._result = iwax.deserialize_transaction(self.file_path.read_bytes())
            return

        raise LoadTransactionError(self, f"Failed to parse transaction from file: {self.file_path}")
