from __future__ import annotations

from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand


@dataclass(kw_only=True)
class ShowTransactionStatus(WorldBasedCommand):
    """
    Show the status of a transaction.

    Args:
        transaction_id: The ID of the transaction to show the status for.
    """

    transaction_id: str

    async def _run(self) -> None:
        """
        Show the status of a transaction.

        Returns:
            None: The method prints the transaction status into the console.
        """
        status = await self.world.commands.find_transaction(transaction_id=self.transaction_id)

        typer.echo(status.result_or_raise)
