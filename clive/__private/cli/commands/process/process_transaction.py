from dataclasses import dataclass
from pathlib import Path

from clive.__private.cli.commands.abc.perform_transaction_command import PerformTransactionCommand
from clive.models import Transaction


@dataclass(kw_only=True)
class ProcessTransaction(PerformTransactionCommand):
    from_file: str

    async def run(self) -> None:
        await super().run()



    async def _get_content(self) -> Transaction:
        return (await self.world.commands.load_transaction_from_file(path=Path(self.from_file))).result_or_raise


