from dataclasses import dataclass
from typing import TYPE_CHECKING

import typer
from rich.console import Console
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.core.commands.data_retrieval.witnesses_data import WitnessesDataRetrieval
from clive.__private.core.formatters.humanize import humanize_datetime

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.witnesses_data import WitnessData, WitnessesData


@dataclass(kw_only=True)
class ShowWitnesses(WorldBasedCommand):
    account_name: str
    page_size: int
    page_no: int

    async def _run(self) -> None:
        response = await self.world.node.api.database_api.find_accounts(accounts=[self.account_name])
        if len(response.accounts) == 0:
            typer.echo(f"Account {self.account_name} not found on node {self.world.node.address}")
            return
        proxy = response.accounts[0].proxy

        wrapper = await self.world.commands.retrieve_witnesses_data(
            account_name=proxy if proxy else self.account_name,
            mode=WitnessesDataRetrieval.DEFAULT_MODE,
            witness_name_pattern=None,
            search_by_name_limit=WitnessesDataRetrieval.DEFAULT_SEARCH_BY_NAME_LIMIT,
        )
        witnesses_data: WitnessesData = wrapper.result_or_raise
        start_index: int = self.page_no * self.page_size
        end_index: int = start_index + self.page_size
        witnesses_list: list[WitnessData] = list(witnesses_data.witnesses.values())
        witnesses_chunk: list[WitnessData] = witnesses_list[start_index:end_index]

        table = Table(title=f"Witnesses and votes of `{proxy if proxy else self.account_name}` account")

        table.add_column("voted", justify="left", style="cyan", overflow="fold")
        table.add_column("rank", justify="right", style="green", overflow="fold")
        table.add_column("witness name", justify="right", style="green", overflow="fold")
        table.add_column("votes", justify="right", style="green", overflow="fold")
        table.add_column("created", justify="right", style="green", overflow="fold")
        table.add_column("missed blocks", justify="right", style="green", overflow="fold")
        table.add_column("last block", justify="right", style="green", overflow="fold")
        table.add_column("price feed", justify="right", style="green", overflow="fold")
        table.add_column("version", justify="right", style="green", overflow="fold")

        witness: WitnessData
        for witness in witnesses_chunk:
            table.add_row(
                f"{witness.voted}",
                f"{witness.rank}",
                f"{witness.name}",
                f"{witness.votes}",
                f"{humanize_datetime(witness.created, with_time=False)}",
                f"{witness.missed_blocks}",
                f"{witness.last_block}",
                f"{witness.price_feed}",
                f"{witness.version}",
            )
        console = Console()
        console.print(table)
