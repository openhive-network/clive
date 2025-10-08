from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli
from clive.__private.cli.table_pagination_info import add_pagination_info_to_table_if_needed
from clive.__private.core.formatters.humanize import humanize_bool
from clive.__private.si.core.show import ShowWitnesses as ShowWitnessesSi

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.witnesses_data import WitnessData


@dataclass(kw_only=True)
class ShowWitnesses(WorldBasedCommand):
    account_name: str
    page_size: int
    page_no: int

    async def _run(self) -> None:
        witnesses_list_len, proxy, witnesses_chunk = await ShowWitnessesSi(
            world=self.world, account_name=self.account_name, page_size=self.page_size, page_no=self.page_no
        ).get_witness_chunk()
        proxy_name_message = f"`{self.account_name}`"
        if proxy:
            proxy_name_message += f" (proxy set to `{proxy}`)"
        table = Table(title=f"Witnesses and votes of {proxy_name_message} account")

        table.add_column("voted", justify="left", style="cyan")
        table.add_column("rank", justify="right", style="green")
        table.add_column("witness name", justify="right", style="green")
        table.add_column("votes", justify="right", style="green", no_wrap=True)
        table.add_column("created", justify="right", style="green")
        table.add_column("missed\nblocks", justify="right", style="green")
        table.add_column("last block", justify="right", style="green")
        table.add_column("price\nfeed", justify="right", style="green")
        table.add_column("version", justify="right", style="green")

        witness: WitnessData
        for witness in witnesses_chunk:
            table.add_row(
                humanize_bool(witness.voted),
                f"{witness.rank}",
                f"{witness.name}",
                f"{witness.votes}",
                f"{witness.pretty_created}",
                f"{witness.missed_blocks}",
                f"{witness.last_block}",
                f"{witness.price_feed}",
                f"{witness.version}",
            )

        add_pagination_info_to_table_if_needed(
            table=table, page_no=self.page_no, page_size=self.page_size, all_entries=witnesses_list_len
        )

        print_cli(table)
