from dataclasses import dataclass

from rich.console import Console
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.core.formatters.humanize import humanize_hbd_exchange_rate


@dataclass(kw_only=True)
class ShowWitness(WorldBasedCommand):
    name: str

    async def _run(self) -> None:
        wrapper = await self.world.commands.find_witness(witness_name=self.name)
        witness = wrapper.result_or_raise

        table = Table(title=f"Details of `{self.name}` witness", show_header=False)

        table.add_row("created", f"{witness.created}")
        table.add_row("url", f"{witness.url}")
        table.add_row("hardfork time vote", f"{witness.hardfork_time_vote}")
        table.add_row("hardfork version vote", f"{witness.hardfork_version_vote}")
        table.add_row("price feed", f"{humanize_hbd_exchange_rate(witness.hbd_exchange_rate)}")
        table.add_row("last confirmed block num", f"{witness.last_confirmed_block_num}")
        table.add_row("last hbd exchange update", f"{witness.last_hbd_exchange_update}")
        table.add_row("last work", f"{witness.last_work}")
        table.add_row("props", f"{witness.props}")
        table.add_row("running version", f"{witness.running_version}")
        table.add_row("signing key", f"{witness.signing_key}")
        table.add_row("total missed", f"{witness.total_missed}")

        console = Console()
        console.print(table)
