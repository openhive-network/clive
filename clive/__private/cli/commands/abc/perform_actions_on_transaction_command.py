from __future__ import annotations

import errno
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import rich
import typer

from clive.__private.cli.commands.abc.forceable_cli_command import ForceableCLICommand
from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import (
    CLIBroadcastCannotBeUsedWithForceUnsignError,
    CLIPrettyError,
    CLITransactionBadAccountError,
    CLITransactionNotSignedError,
    CLITransactionToExchangeError,
    CLITransactionUnknownAccountError,
)
from clive.__private.core.commands.sign import ALREADY_SIGNED_MODE_DEFAULT, AlreadySignedMode
from clive.__private.core.ensure_transaction import ensure_transaction
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.core.keys.key_manager import KeyNotFoundError
from clive.__private.validators.exchange_operations_validator import ExchangeOperationsValidatorCli
from clive.__private.validators.path_validator import PathValidator

if TYPE_CHECKING:
    from clive.__private.core.ensure_transaction import TransactionConvertibleType
    from clive.__private.core.keys import PublicKey
    from clive.__private.models import Transaction


@dataclass(kw_only=True)
class PerformActionsOnTransactionCommand(WorldBasedCommand, ForceableCLICommand, ABC):
    sign: str | None = None
    already_signed_mode: AlreadySignedMode = ALREADY_SIGNED_MODE_DEFAULT
    force_unsign: bool = False
    save_file: str | Path | None = None
    broadcast: bool = False

    @property
    def save_file_path(self) -> Path | None:
        return Path(self.save_file) if self.save_file is not None else None

    @abstractmethod
    async def _get_transaction_content(self) -> TransactionConvertibleType:
        """Get the transaction content to be processed."""

    async def get_transaction(self) -> Transaction:
        return ensure_transaction(await self._get_transaction_content())

    async def validate(self) -> None:
        self._validate_save_file_path()
        await super().validate()

    async def validate_inside_context_manager(self) -> None:
        await self._validate_bad_accounts()
        if self.profile.should_enable_known_accounts:
            await self._validate_unknown_accounts()
        await self._validate_operations_to_exchange()
        await super().validate_inside_context_manager()

    async def _run(self) -> None:
        if not self.broadcast:
            typer.echo("[Performing dry run, because --broadcast is not set.]\n")

        transaction = (
            await self.world.commands.perform_actions_on_transaction(
                content=await self._get_transaction_content(),
                sign_key=self.__get_key_to_sign(),
                already_signed_mode=self.already_signed_mode,
                force_unsign=self.force_unsign,
                save_file_path=self.save_file_path,
                broadcast=self.broadcast,
            )
        ).result_or_raise

        self.__print_transaction(transaction.with_hash())
        typer.echo(
            "Transaction was successfully"
            f" {'broadcasted' if self.broadcast else self._get_transaction_created_message()}."
        )
        if self.save_file is not None:
            typer.echo(f"Transaction was saved to {self.save_file}")

    def __get_key_to_sign(self) -> PublicKey | None:
        if self.sign is None:
            return None

        try:
            return self.profile.keys.get_from_alias(self.sign)
        except KeyNotFoundError:
            raise CLIPrettyError(
                f"Key `{self.sign}` was not found in the working account keys.", errno.ENOENT
            ) from None

    def _validate_save_file_path(self) -> None:
        if self.save_file:
            result = PathValidator(mode="can_be_file").validate(str(self.save_file))
            if not result.is_valid:
                raise CLIPrettyError(f"Can't save to file: {humanize_validation_result(result)}", errno.EINVAL)

    def _validate_if_broadcast_is_used_without_force_unsign(self) -> None:
        if self.broadcast and self.force_unsign:
            raise CLIBroadcastCannotBeUsedWithForceUnsignError

    def _validate_if_broadcasting_signed_transaction(self) -> None:
        if self.broadcast and not self.sign:
            raise CLITransactionNotSignedError

    async def _validate_unknown_accounts(self) -> None:
        transaction_ensured = await self.get_transaction()
        unknown_accounts = transaction_ensured.get_unknown_accounts(self.profile.accounts.known)
        if unknown_accounts:
            raise CLITransactionUnknownAccountError(*unknown_accounts)

    async def _validate_bad_accounts(self) -> None:
        transaction_ensured = await self.get_transaction()
        bad_accounts = transaction_ensured.get_bad_accounts(self.profile.accounts.get_bad_accounts())
        if bad_accounts:
            raise CLITransactionBadAccountError(*bad_accounts)

    async def _validate_operations_to_exchange(self) -> None:
        transaction_ensured = await self.get_transaction()
        exchange_operation_validator = ExchangeOperationsValidatorCli(
            transaction=transaction_ensured,
            suppress_force_validation=self.force,
        )
        for exchange in self.world.known_exchanges:
            result = exchange_operation_validator.validate(exchange.name)
            if not result.is_valid:
                raise CLITransactionToExchangeError(humanize_validation_result(result))

    def _get_transaction_created_message(self) -> str:
        return "created"

    def __print_transaction(self, transaction: Transaction) -> None:
        transaction_json = transaction.json(by_alias=True)
        message = self._get_transaction_created_message().capitalize()
        typer.echo(f"{message} transaction:")
        rich.print_json(transaction_json)
