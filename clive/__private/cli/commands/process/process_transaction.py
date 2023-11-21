import errno
from dataclasses import dataclass
from pathlib import Path

from clive.__private.cli.commands.abc.perform_actions_on_transaction_command import PerformActionsOnTransactionCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.models import Transaction


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
        return (await self.world.commands.load_transaction_from_file(path=self.from_file_path)).result_or_raise

    async def _get_transaction_content(self) -> Transaction:
        return await self.__loaded_transaction

    def _get_transaction_created_message(self) -> str:
        return "loaded"

    async def _validate_options(self) -> None:
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
        self._validate_if_sign_and_password_are_used_together()
        self._validate_if_broadcast_is_used_without_force_unsign()

        transaction = await self.__loaded_transaction
        self.__validate_signed_transaction() if transaction.is_signed() else self.__validate_unsigned_transaction()

    def __validate_signed_transaction(self) -> None:
        if self.already_signed_mode == "error" and self.sign:
            raise CLIPrettyError("You cannot sign a transaction that is already signed.", errno.EINVAL)

    def __validate_unsigned_transaction(self) -> None:
        self._validate_if_broadcast_is_used_with_sign_and_password()