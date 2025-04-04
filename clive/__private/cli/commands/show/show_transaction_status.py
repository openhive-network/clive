from __future__ import annotations

from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand


@dataclass(kw_only=True)
class ShowTransactionStatus(WorldBasedCommand):
    transaction_id: str

    async def _run(self) -> None:
        status = await self.world.commands.find_transaction(transaction_id=self.transaction_id)

        typer.echo(status.result_or_raise)
