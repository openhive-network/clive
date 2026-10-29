from __future__ import annotations

import contextlib
import json
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
        with contextlib.suppress(JSONDecodeError, UnicodeDecodeError):
            data = json.loads(self.file_path.read_text())
            if self._is_transaction(data):
                self._result = Transaction.from_builtins(data)
                return

        with contextlib.suppress(WaxOperationFailedError, UnicodeDecodeError, JSONDecodeError):
            self._result = iwax.deserialize_transaction(self.file_path.read_bytes())
            return

        raise LoadTransactionError(self, f"Failed to parse transaction from file: {self.file_path}")

    @staticmethod
    def _is_transaction(data: object) -> bool:
        """
        Check whether the data is a transaction in the HF26 form.

        Models are built without validation, so the data is validated with the validation model of transactions. Fields
        missing in the data take their default values, as when the transaction is built.

        Args:
            data: JSON builtins of the file.

        Returns:
            True when the data is a valid transaction, False otherwise.
        """
        # imported here, models for validation are loaded only when needed
        from hiveio_api._validation.operations import Transaction as TransactionValidationModel  # noqa: PLC0415
        from hiveio_api.validation import validate  # noqa: PLC0415

        if not isinstance(data, dict):
            return False
        return not validate({**Transaction().to_builtins(), **data}, TransactionValidationModel)
