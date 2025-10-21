from __future__ import annotations

import errno
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.perform_actions_on_transaction_command import PerformActionsOnTransactionCommand
from clive.__private.cli.exceptions import (
    CLIPrettyError,
)
from clive.__private.core.commands.load_transaction import LoadTransaction
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.validators.path_validator import PathValidator

if TYPE_CHECKING:
    from clive.__private.models.transaction import Transaction


@dataclass(kw_only=True)
class ProcessTransaction(PerformActionsOnTransactionCommand):
    from_file: str | Path
    _loaded_transaction: Transaction | None = None

    @property
    def from_file_path(self) -> Path:
        return Path(self.from_file)

    @property
    async def __loaded_transaction(self) -> Transaction:
        if self._loaded_transaction is None:
            self._loaded_transaction = await self.__load_transaction()
        return self._loaded_transaction

    async def validate(self) -> None:
        self._validate_from_file_argument()
        await super().validate()

    def _validate_from_file_argument(self) -> None:
        result = PathValidator(mode="is_file").validate(str(self.from_file))
        if not result.is_valid:
            raise CLIPrettyError(
                f"Can't load transaction from file: {humanize_validation_result(result)}", errno.EINVAL
            )

    async def _is_transaction_already_signed(self) -> bool:
        return (await self.__loaded_transaction).is_signed

    async def _get_transaction_content(self) -> Transaction:
        return await self.__loaded_transaction

    def _get_transaction_created_message(self) -> str:
        return "loaded"

    async def __load_transaction(self) -> Transaction:
        return await LoadTransaction(file_path=self.from_file_path).execute_with_result()
