from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli


@dataclass(kw_only=True)
class ShowTransactionStatus(WorldBasedCommand):
    transaction_id: str

    async def _run(self) -> None:
        status = await self.world.commands.find_transaction(transaction_id=self.transaction_id)

        print_cli(str(status.result_or_raise))
