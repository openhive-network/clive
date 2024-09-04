import errno
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import rich
import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import (
    CLIBroadcastCannotBeUsedWithForceUnsignError,
    CLIBroadcastRequiresSignKeyAndPasswordError,
    CLIPrettyError,
    CLISigningRequiresAPasswordError,
)
from clive.__private.core.commands.sign import ALREADY_SIGNED_MODE_DEFAULT, AlreadySignedMode
from clive.__private.core.ensure_transaction import TransactionConvertibleType
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.core.keys import PublicKey
from clive.__private.core.keys.key_manager import KeyNotFoundError
from clive.__private.models import Transaction
from clive.__private.settings import safe_settings
from clive.__private.validators.path_validator import PathValidator


@dataclass(kw_only=True)
class PerformActionsOnTransactionCommand(WorldBasedCommand, ABC):
    password: str | None = None
    sign: str | None = None
    already_signed_mode: AlreadySignedMode = ALREADY_SIGNED_MODE_DEFAULT
    force_unsign: bool = False
    save_file: str | Path | None = None
    broadcast: bool = False

    @property
    def password_ensure(self) -> str:
        assert self.password is not None, "Password is required at this point."
        return self.password

    @property
    def save_file_path(self) -> Path | None:
        return Path(self.save_file) if self.save_file is not None else None

    @abstractmethod
    async def _get_transaction_content(self) -> TransactionConvertibleType:
        """Get the transaction content to be processed."""

    async def validate(self) -> None:
        if not self.save_file:
            return

        result = PathValidator(mode="can_be_file").validate(str(self.save_file))
        if not result.is_valid:
            raise CLIPrettyError(f"Can't save to file: {humanize_validation_result(result)}", errno.EINVAL)

    async def _configure_inside_context_manager(self) -> None:
        await self._configure_wallet()
        await super()._configure_inside_context_manager()

    async def _configure(self) -> None:
        self.use_beekeeper = self.__is_beekeeper_required()

    async def _configure_wallet(self) -> None:
        if self.__is_beekeeper_required() and not safe_settings.beekeeper.is_session_token_set:
            await self.world.commands.unlock(password=self.password_ensure)

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
            return self.world.profile.keys.get(self.sign)
        except KeyNotFoundError:
            raise CLIPrettyError(
                f"Key `{self.sign}` was not found in the working account keys.", errno.ENOENT
            ) from None

    async def validate_inside_context_manager(self) -> None:
        self._validate_if_wallet_is_unlocked()
        await super().validate_inside_context_manager()

    def _validate_if_wallet_is_unlocked(self) -> None:
        if (
            self.__is_beekeeper_required()
            and safe_settings.beekeeper.is_session_token_set
            and not self.world.app_state.is_unlocked
        ):
            raise CLIWalletIsNotUnlockedError

    def _validate_if_sign_and_password_are_used_together(self) -> None:
        if safe_settings.beekeeper.is_session_token_set is False and (self.sign is not None and self.password is None):
            raise CLISigningRequiresAPasswordError

    def _validate_if_broadcast_is_used_without_force_unsign(self) -> None:
        if self.broadcast and self.force_unsign:
            raise CLIBroadcastCannotBeUsedWithForceUnsignError

    def _validate_if_broadcast_is_used_with_sign_and_password(self) -> None:
        if (
            safe_settings.beekeeper.is_session_token_set is False
            and self.broadcast
            and (self.sign is None or self.password is None)
        ):
            raise CLIBroadcastRequiresSignKeyAndPasswordError

    def _get_transaction_created_message(self) -> str:
        return "created"

    def __print_transaction(self, transaction: Transaction) -> None:
        transaction_json = transaction.json(by_alias=True)
        message = self._get_transaction_created_message().capitalize()
        typer.echo(f"{message} transaction:")
        rich.print_json(transaction_json)

    def __is_beekeeper_required(self) -> bool:
        return bool(self.sign) and (bool(self.password) or safe_settings.beekeeper.is_session_token_set)
