import errno
from dataclasses import dataclass
from pathlib import Path

from clive.__private.cli.commands.abc.perform_actions_on_transaction_command import PerformActionsOnTransactionCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.commands.load_transaction import LoadTransaction
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.models import Transaction
from clive.__private.validators.path_validator import PathValidator


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

    async def __load_transaction(self) -> Transaction:
        return await LoadTransaction(file_path=self.from_file_path).execute_with_result()

    async def _get_transaction_content(self) -> Transaction:
        return await self.__loaded_transaction

    def _get_transaction_created_message(self) -> str:
        return "loaded"

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
        if self.already_signed_mode == "error" and self.sign:
            raise CLIPrettyError("You cannot sign a transaction that is already signed.", errno.EINVAL)

    def _validate_from_file_argument(self) -> None:
        result = PathValidator(mode="is_file").validate(str(self.from_file))
        if not result.is_valid:
            raise CLIPrettyError(
                f"Can't load transaction from file: {humanize_validation_result(result)}", errno.EINVAL
            )

    async def _is_transaction_signed(self) -> bool:
        return (await self.__loaded_transaction).is_signed
