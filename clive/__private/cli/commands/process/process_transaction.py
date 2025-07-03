from __future__ import annotations

import errno
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.perform_actions_on_transaction_command import PerformActionsOnTransactionCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.commands.load_transaction import LoadTransaction
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.validators.path_validator import PathValidator

if TYPE_CHECKING:
    from clive.__private.models import Transaction


@dataclass(kw_only=True)
class ProcessTransaction(PerformActionsOnTransactionCommand):
    """
    Class to process a transaction by loading it from a file and performing actions on it.

    Args:
        from_file: Path to the file containing the transaction.
        _loaded_transaction: Cached loaded transaction object.
    """

    from_file: str | Path
    _loaded_transaction: Transaction | None = None

    @property
    def from_file_path(self) -> Path:
        """
        Return the path to the file from which the transaction will be loaded.

        Returns:
            Path: The path to the transaction file.
        """
        return Path(self.from_file)

    @property
    async def __loaded_transaction(self) -> Transaction:
        """
        Return the loaded transaction, loading it from the file if not already loaded.

        If the transaction is already loaded, it returns the cached transaction object.

        Returns:
            Transaction: The loaded transaction object.
        """
        if self._loaded_transaction is None:
            self._loaded_transaction = await self.__load_transaction()
        return self._loaded_transaction

    async def validate(self) -> None:
        """
        Validate given options before taking any action.

        User may:
        1. Load already signed transaction:
         - broadcast it right away (no need to specify sign_key and password)
         - save it to file in the same or different format (.bin/.json),
           as it is (signed - sign_key and password required) or remove its signature (force-unsign)
        2. Load unsigned transaction:
          - broadcast it (but sign_key and password must be provided)
          - save it to file in the same or different format (in .bin/.json format):
            * if sign_key is provided, it will be signed and saved
            * if sign_key is not provided, it will be saved as unsigned.

        """
        self._validate_if_broadcast_is_used_without_force_unsign()
        self._validate_signed_transaction() if await (
            self._is_transaction_signed()
        ) else self._validate_if_broadcasting_signed_transaction()
        self._validate_from_file_argument()
        await super().validate()

    def _validate_signed_transaction(self) -> None:
        """
        Validate if the transaction is already signed and if the user is trying to sign it again.

        Raises:
            CLIPrettyError: If the transaction is already signed and the user tries to sign it again.

        Returns:
            None
        """
        if self.already_signed_mode == "error" and self.sign:
            raise CLIPrettyError("You cannot sign a transaction that is already signed.", errno.EINVAL)

    def _validate_from_file_argument(self) -> None:
        """
        Validate the 'from_file' argument to ensure it points to a valid file.

        Raises:
            CLIPrettyError: If the 'from_file' argument does not point to a valid file.

        Returns:
            None
        """
        result = PathValidator(mode="is_file").validate(str(self.from_file))
        if not result.is_valid:
            raise CLIPrettyError(
                f"Can't load transaction from file: {humanize_validation_result(result)}", errno.EINVAL
            )

    async def _is_transaction_signed(self) -> bool:
        """
        Check if the loaded transaction is signed.

        Returns:
            bool: True if the transaction is signed, False otherwise.
        """
        return (await self.__loaded_transaction).is_signed

    async def _get_transaction_content(self) -> Transaction:
        """
        Get the content of the loaded transaction.

        Returns:
            Transaction: The loaded transaction object.
        """
        return await self.__loaded_transaction

    def _get_transaction_created_message(self) -> str:
        """
        Return a message indicating that the transaction has been loaded successfully.

        Returns:
            str: A message indicating the transaction has been loaded.
        """
        return "loaded"

    async def __load_transaction(self) -> Transaction:
        """
        Load the transaction from the specified file path.

        Returns:
            Transaction: The loaded transaction object.
        """
        return await LoadTransaction(file_path=self.from_file_path).execute_with_result()
