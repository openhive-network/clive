from __future__ import annotations

import errno
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final, cast

from clive.__private.cli.commands.abc.forceable_cli_command import ForceableCLICommand
from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import (
    CLIKeyAliasNotFoundError,
    CLIMultipleKeysAutoSignError,
    CLINoKeysAvailableError,
    CLIPrettyError,
    CLITransactionAlreadySignedError,
    CLITransactionBadAccountError,
    CLITransactionNotSignedError,
    CLITransactionToExchangeError,
    CLITransactionUnknownAccountError,
    CLIWrongAlreadySignedModeAutoSignError,
)
from clive.__private.cli.print_cli import print_cli, print_json
from clive.__private.cli.warnings import typer_echo_warnings
from clive.__private.core.commands.perform_actions_on_transaction import AutoSignSkippedWarning
from clive.__private.core.constants.data_retrieval import ALREADY_SIGNED_MODE_DEFAULT
from clive.__private.core.ensure_transaction import ensure_transaction
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.core.keys.key_manager import MultipleKeysFoundError
from clive.__private.validators.exchange_operations_validator import ExchangeOperationsValidatorCli
from clive.__private.validators.path_validator import PathValidator

if TYPE_CHECKING:
    from clive.__private.core.ensure_transaction import TransactionConvertibleType
    from clive.__private.core.keys import PublicKey
    from clive.__private.core.types import AlreadySignedMode
    from clive.__private.models.transaction import Transaction


class AutoSignSkippedWarningCLI(Warning):
    """
    Raised when autosign is skipped because the transaction is already signed.

    Attributes:
        MESSAGE: The warning message.
    """

    MESSAGE: Final[str] = (
        "Your transaction is already signed. Autosign will be skipped. If you want to multisign your "
        "transaction, use '--sign-with' together with '--already-signed-mode multisign'. "
        "For more information, check 'clive process transaction -h'"
    )

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


@dataclass(kw_only=True)
class PerformActionsOnTransactionCommand(WorldBasedCommand, ForceableCLICommand, ABC):
    sign_with: str | None = None
    autosign: bool | None = None
    already_signed_mode: AlreadySignedMode = ALREADY_SIGNED_MODE_DEFAULT
    force_unsign: bool = False
    save_file: str | Path | None = None
    broadcast: bool | None = None
    _transaction: Transaction | None = None

    @abstractmethod
    async def _get_transaction_content(self) -> TransactionConvertibleType:
        """Get the transaction content to be processed into a transaction."""

    @property
    def is_sign_with_given(self) -> bool:
        return self.sign_with is not None

    @property
    def sign_with_ensure(self) -> str:
        assert self.sign_with is not None, "Expected sign_with to be set"
        return self.sign_with

    @property
    def sign_key(self) -> PublicKey | None:
        if not self.is_sign_with_given:
            return None
        return self.profile.keys.get_from_alias(self.sign_with_ensure)

    @property
    def is_autosign_explicitly_requested(self) -> bool:
        return self.autosign is True

    @property
    def use_autosign(self) -> bool:
        return self.is_autosign_explicitly_requested or (self.autosign is None and not self.is_sign_with_given)

    @property
    async def should_be_signed(self) -> bool:
        if self.force_unsign:
            # force_unsign removes signatures and no signing happens when given
            return False

        if self.is_transaction_signed:
            if self.use_autosign:
                # autosign is about to be skipped when transaction is already signed
                return False

            # signing happens in different already_signed_mode than strict when sign_with is given
            return self.is_sign_with_given and self.already_signed_mode != "strict"

        return self.use_autosign or self.is_sign_with_given

    @property
    def is_save_file_given(self) -> bool:
        return self.save_file is not None

    @property
    def save_file_path(self) -> Path | None:
        return Path(cast("str | Path", self.save_file)) if self.is_save_file_given else None

    @property
    def is_broadcast_given(self) -> bool:
        return self.broadcast is not None

    @property
    def is_broadcast_explicitly_requested(self) -> bool:
        return self.broadcast is True

    @property
    def should_broadcast(self) -> bool:
        if self.is_broadcast_given:
            return cast("bool", self.broadcast)

        # Broadcast by default if not saving to file and not forcing unsign
        return not self.is_save_file_given and not self.force_unsign

    @property
    def transaction(self) -> Transaction:
        assert self._transaction is not None, (
            "Transaction not available yet. Is available after entering context manager."
        )
        return self._transaction

    @property
    def is_transaction_signed(self) -> bool:
        return self.transaction.is_signed

    async def validate(self) -> None:
        self.validate_all_mutually_exclusive_options()
        self._validate_already_signed_mode()
        self._validate_save_file_path()
        await super().validate()

    def validate_all_mutually_exclusive_options(self) -> None:
        self._validate_mutually_exclusive(
            autosign=self.is_autosign_explicitly_requested, force_unsign=self.force_unsign
        )
        self._validate_mutually_exclusive(sign_with=self.is_sign_with_given, force_unsign=self.force_unsign)
        self._validate_mutually_exclusive(
            autosign=self.is_autosign_explicitly_requested, sign_with=self.is_sign_with_given
        )
        self._validate_if_broadcast_is_used_without_force_unsign()
        super().validate_all_mutually_exclusive_options()

    async def validate_inside_context_manager(self) -> None:
        self._validate_manual_sign_not_allowed_in_strict_already_signed_mode()
        self._validate_if_broadcasting_signed_transaction()
        await self._validate_bad_accounts()
        await self._validate_unknown_accounts()
        await self._validate_operations_to_exchange()
        await self._validate_keys_availability()
        await super().validate_inside_context_manager()

    async def _hook_after_fetching_data(self) -> None:
        if self._transaction is None:
            self._transaction = await self._get_transaction()
        await super()._hook_after_fetching_data()

    async def _run(self) -> None:
        self._print_dry_run_message_if_needed()

        with typer_echo_warnings(AutoSignSkippedWarning, AutoSignSkippedWarningCLI()):
            transaction = (
                await self.world.commands.perform_actions_on_transaction(
                    content=self.transaction,
                    sign_key=self.sign_key,
                    already_signed_mode=self.already_signed_mode,
                    force_unsign=self.force_unsign,
                    save_file_path=self.save_file_path,
                    broadcast=self.should_broadcast,
                    autosign=self.use_autosign,
                )
            ).result_or_raise

        self._print_transaction(transaction.with_hash())
        self._print_transaction_success_message()
        self._print_saved_to_file_message_if_needed()

    async def _get_transaction(self) -> Transaction:
        # transaction can be created only after applying dynamic defaults for working accounts
        # and after required data is fetched
        return ensure_transaction(await self._get_transaction_content())

    def _validate_if_broadcast_is_used_without_force_unsign(self) -> None:
        details = (
            "\n"
            "If you want to broadcast the transaction, don't remove the signature - "
            "remove the '--force-unsign' option.\n"
            "If you want to remove the signature and show or save the unsigned transaction, "
            "add the '--no-broadcast' option."
        )
        self._validate_mutually_exclusive(
            broadcast=self.is_broadcast_explicitly_requested, force_unsign=self.force_unsign, details=details
        )

    def _validate_already_signed_mode(self) -> None:
        if self.use_autosign and self.already_signed_mode in ["override", "multisign"]:
            raise CLIWrongAlreadySignedModeAutoSignError

    def _validate_manual_sign_not_allowed_in_strict_already_signed_mode(self) -> None:
        if self.is_transaction_signed and self.already_signed_mode == "strict" and self.is_sign_with_given:
            raise CLITransactionAlreadySignedError

    def _validate_save_file_path(self) -> None:
        if self.save_file:
            result = PathValidator(mode="can_be_file").validate(str(self.save_file))
            if not result.is_valid:
                raise CLIPrettyError(f"Can't save to file: {humanize_validation_result(result)}", errno.EINVAL)

    def _validate_if_broadcasting_signed_transaction(self) -> None:
        if self.is_transaction_signed:
            return

        if self.should_broadcast and (not self.is_sign_with_given and not self.use_autosign):
            raise CLITransactionNotSignedError

    async def _validate_unknown_accounts(self) -> None:
        if not self.profile.should_enable_known_accounts:
            return

        unknown_accounts = self.transaction.get_unknown_accounts(self.profile.accounts.known)
        if unknown_accounts:
            raise CLITransactionUnknownAccountError(*unknown_accounts)

    async def _validate_bad_accounts(self) -> None:
        bad_accounts = self.transaction.get_bad_accounts(self.profile.accounts.get_bad_accounts())
        if bad_accounts:
            raise CLITransactionBadAccountError(*bad_accounts)

    async def _validate_operations_to_exchange(self) -> None:
        exchange_operation_validator = ExchangeOperationsValidatorCli(
            transaction=self.transaction,
            should_validate_for_unsafe_exchange_operations=not self.force,
        )
        for exchange in self.world.known_exchanges:
            result = exchange_operation_validator.validate(exchange.name)
            if not result.is_valid:
                raise CLITransactionToExchangeError(humanize_validation_result(result))

    async def _validate_keys_availability(self) -> None:
        if not await self.should_be_signed:
            return

        if len(self.profile.keys) == 0:
            raise CLINoKeysAvailableError

        if self.is_sign_with_given and self.profile.keys.is_alias_available(self.sign_with_ensure):
            raise CLIKeyAliasNotFoundError(self.sign_with_ensure)

        if self.use_autosign:
            try:
                _ = self.profile.keys.unique_key
            except MultipleKeysFoundError:
                raise CLIMultipleKeysAutoSignError from None

    def _get_transaction_created_message(self) -> str:
        return "created"

    def _print_transaction(self, transaction: Transaction) -> None:
        transaction_json = transaction.json(order="sorted")
        message = self._get_transaction_created_message().capitalize()
        print_cli(f"{message} transaction:")
        print_json(transaction_json)

    def _print_dry_run_message_if_needed(self) -> None:
        if not self.should_broadcast and not self.is_save_file_given:
            print_cli("[Performing dry run, because no broadcast or save to file was requested.]\n")

    def _print_transaction_success_message(self) -> None:
        print_cli(
            "Transaction was successfully"
            f" {'broadcasted' if self.should_broadcast else self._get_transaction_created_message()}."
        )

    def _print_saved_to_file_message_if_needed(self) -> None:
        if self.save_file is not None:
            print_cli(f"Transaction was saved to {self.save_file}")
