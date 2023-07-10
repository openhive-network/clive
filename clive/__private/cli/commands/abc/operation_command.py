from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import rich
import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.core.perform_actions_on_transaction import perform_actions_on_transaction


@dataclass(kw_only=True)
class OperationCommand(WorldBasedCommand, ABC):
    from clive.models import Operation, Transaction

    sign: str
    save_file: str | None
    broadcast: bool

    @abstractmethod
    def _create_operation(self) -> Operation:
        """Create the operation."""

    def run(self) -> None:
        key_to_sign = self.world.profile_data.working_account.keys.get(self.sign)

        transaction = perform_actions_on_transaction(
            content=self._create_operation(),
            beekeeper=self.world.beekeeper,
            node=self.world.node,
            sign_key=key_to_sign,
            save_file_path=Path(self.save_file) if self.save_file is not None else None,
            broadcast=self.broadcast,
            chain_id=self.world.node.chain_id,
        )

        self.__print_transaction(transaction)
        typer.echo(f"Transaction was successfully {'broadcasted' if self.broadcast else 'created'}.")

    @staticmethod
    def __print_transaction(transaction: Transaction) -> None:
        transaction_json = transaction.json(by_alias=True)
        typer.echo("Created transaction:")
        rich.print_json(transaction_json)
