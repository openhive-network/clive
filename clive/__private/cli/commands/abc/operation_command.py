from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import rich
import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli_error import CLIError
from clive.__private.core.keys.key_manager import KeyNotFoundError
from clive.__private.core.perform_actions_on_transaction import perform_actions_on_transaction
from clive.models import Operation, Transaction


@dataclass(kw_only=True)
class OperationCommand(WorldBasedCommand, ABC):
    sign: str
    save_file: str | None
    broadcast: bool

    @abstractmethod
    def _create_operation(self) -> Operation:
        """Create the operation."""

    async def run(self) -> None:
        try:
            key_to_sign = self.world.profile_data.working_account.keys.get(self.sign)
        except KeyNotFoundError:
            raise CLIError(f"Key `{self.sign}` was not found in the working account keys.") from None

        transaction = await perform_actions_on_transaction(
            content=self._create_operation(),
            app_state=self.world.app_state,
            beekeeper=self.world.beekeeper,
            node=self.world.node,
            sign_key=key_to_sign,
            save_file_path=Path(self.save_file) if self.save_file is not None else None,
            broadcast=self.broadcast,
            chain_id=(await self.world.node.chain_id),
        )

        self.__print_transaction(transaction.with_hash())
        typer.echo(f"Transaction was successfully {'broadcasted' if self.broadcast else 'created'}.")

    @staticmethod
    def __print_transaction(transaction: Transaction) -> None:
        transaction_json = transaction.json(by_alias=True)
        typer.echo("Created transaction:")
        rich.print_json(transaction_json)
