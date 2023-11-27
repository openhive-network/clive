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
from clive.__private.core.keys import PublicKey
from clive.__private.core.keys.key_manager import KeyNotFoundError
from clive.models import Transaction


@dataclass(kw_only=True)
class PerformActionsOnTransactionCommand(WorldBasedCommand, ABC):
    password: str | None = None
    sign: str | None = None
    already_signed_mode: AlreadySignedMode = ALREADY_SIGNED_MODE_DEFAULT
    force_unsign: bool = False
    chain_id: str | None = None
    """The chain ID to use when signing the transaction. If not provided, the one from settings.toml config and
    then from the node get_config api will be used as fallback."""
    save_file: str | Path | None = None
    broadcast: bool = False

    @property
    def save_file_path(self) -> Path | None:
        return Path(self.save_file) if self.save_file is not None else None

    @abstractmethod
    async def _get_transaction_content(self) -> TransactionConvertibleType:
        """Get the transaction content to be processed."""

    async def _run(self) -> None:
        await self._validate_options()

        if not self.broadcast:
            typer.echo("[Performing dry run, because --broadcast is not set.]\n")

        if self.password is not None:
            await self.world.commands.activate(password=self.password)

        transaction = (
            await self.world.commands.perform_actions_on_transaction(
                content=await self._get_transaction_content(),
                sign_key=self.__get_key_to_sign(),
                already_signed_mode=self.already_signed_mode,
                force_unsign=self.force_unsign,
                chain_id=self.chain_id,
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
            return self.world.profile_data.working_account.keys.get(self.sign)
        except KeyNotFoundError:
            raise CLIPrettyError(
                f"Key `{self.sign}` was not found in the working account keys.", errno.ENOENT
            ) from None

    async def _validate_options(self) -> None:
        """If you want to validate options before taking any action, override this method."""

    def _validate_if_sign_and_password_are_used_together(self) -> None:
        if self.sign is not None and self.password is None:
            raise CLISigningRequiresAPasswordError

    def _validate_if_broadcast_is_used_without_force_unsign(self) -> None:
        if self.broadcast and self.force_unsign:
            raise CLIBroadcastCannotBeUsedWithForceUnsignError

    def _validate_if_broadcast_is_used_with_sign_and_password(self) -> None:
        if self.broadcast and (self.sign is None or self.password is None):
            raise CLIBroadcastRequiresSignKeyAndPasswordError

    def _get_transaction_created_message(self) -> str:
        return "created"

    def __print_transaction(self, transaction: Transaction) -> None:
        transaction_json = transaction.json(by_alias=True)
        message = self._get_transaction_created_message().capitalize()
        typer.echo(f"{message} transaction:")
        rich.print_json(transaction_json)
