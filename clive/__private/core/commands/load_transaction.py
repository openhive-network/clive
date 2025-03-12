from __future__ import annotations

import contextlib
from dataclasses import dataclass
from json import JSONDecodeError
from typing import TYPE_CHECKING

from clive.__private.core import iwax
from clive.__private.core.commands.abc.command import CommandError
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.iwax import WaxOperationFailedError
from clive.__private.models import Transaction
from schemas.decoders import get_hf26_decoder

if TYPE_CHECKING:
    from pathlib import Path


class LoadTransactionError(CommandError):
    pass


@dataclass(kw_only=True)
class LoadTransaction(CommandWithResult[Transaction]):
    file_path: Path

    async def _execute(self) -> None:
        with contextlib.suppress(JSONDecodeError, Exception):
            self._result = Transaction.parse_file(path=self.file_path, decoder_factory=get_hf26_decoder)
            return

        with contextlib.suppress(WaxOperationFailedError, JSONDecodeError, Exception):
            self._result = iwax.deserialize_transaction(self.file_path.read_bytes(), decoder_factory=get_hf26_decoder)
            return

        raise LoadTransactionError(self, f"Failed to parse transaction from file: {self.file_path}")
