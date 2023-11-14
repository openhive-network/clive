import errno
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import rich
import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.keys import PublicKey
from clive.__private.core.keys.key_manager import KeyNotFoundError
from clive.__private.core.perform_actions_on_transaction import perform_actions_on_transaction
from clive.models import Operation, Transaction


@dataclass(kw_only=True)
class OperationCommand(WorldBasedCommand, ABC):
    password: str | None
    sign: str | None
    save_file: str | None
    broadcast: bool

    @abstractmethod
    def _create_operation(self) -> Operation:
        """Create the operation."""

    async def run(self) -> None:
        self.__validate_options()

        if not self.broadcast:
            typer.echo("[Performing dry run, because --broadcast is not set.]\n")

        await super().run()

    async def _run(self) -> None:
        if self.password is not None:
            await self.world.commands.activate(password=self.password)

        transaction = await perform_actions_on_transaction(
            content=self._create_operation(),
            app_state=self.world.app_state,
            beekeeper=self.world.beekeeper,
            node=self.world.node,
            sign_key=self.__get_key_to_sign(),
            save_file_path=Path(self.save_file) if self.save_file is not None else None,
            broadcast=self.broadcast,
            chain_id=(await self.world.node.chain_id),
        )

        self.__print_transaction(transaction.with_hash())
        typer.echo(f"Transaction was successfully {'broadcasted' if self.broadcast else 'created'}.")
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

    def __validate_options(self) -> None:
        if self.broadcast and self.sign is None:
            raise CLIPrettyError(
                "You must provide a key alias to sign the transaction with if you want to broadcast them."
            )

        if self.sign is not None and self.password is None:
            raise CLIPrettyError("You must provide a password so wallet can be unlocked while signing a transaction.")

    @staticmethod
    def __print_transaction(transaction: Transaction) -> None:
        transaction_json = transaction.json(by_alias=True)
        typer.echo("Created transaction:")
        rich.print_json(transaction_json)
