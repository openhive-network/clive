from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli
from clive.__private.cli.table_pagination_info import add_pagination_info_to_table_if_needed
from clive.__private.core.formatters.humanize import humanize_bool
from clive.__private.py.foundation.show import ShowWitnesses as ShowWitnessesPy

if TYPE_CHECKING:
    from clive.__private.py.data_classes import Witness


@dataclass(kw_only=True)
class ShowWitnesses(WorldBasedCommand):
    account_name: str
    page_size: int
    page_no: int

    async def _run(self) -> None:
        result = await ShowWitnessesPy(
            world=self.world, account_name=self.account_name, page_size=self.page_size, page_no=self.page_no
        ).run()

        proxy_name_message = f"`{self.account_name}`"
        if result.proxy:
            proxy_name_message += f" (proxy set to `{result.proxy}`)"
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

        witness: Witness
        for witness in result.witnesses:
            table.add_row(
                humanize_bool(witness.voted),
                f"{witness.rank}",
                f"{witness.witness_name}",
                f"{witness.votes}",
                f"{witness.created}",
                f"{witness.missed_blocks}",
                f"{witness.last_block}",
                f"{witness.price_feed}",
                f"{witness.version}",
            )

        add_pagination_info_to_table_if_needed(
            table=table, page_no=self.page_no, page_size=self.page_size, all_entries=result.total_count
        )

        print_cli(table)
