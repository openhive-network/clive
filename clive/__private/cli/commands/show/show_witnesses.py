from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.core.commands.data_retrieval.witnesses_data import WitnessesDataRetrieval

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.witnesses_data import WitnessesData, WitnessData


@dataclass(kw_only=True)
class ShowWitnesses(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        if self.world.profile_data.working_account.name == self.account_name:
            proxy = self.world.profile_data.working_account.data.proxy
        else:
            core_account = await self.world.node.api.database_api.find_accounts(accounts=[self.account_name])
            proxy = core_account.proxy

        wrapper = await self.world.commands.retrieve_witnesses_data(
            account_name=proxy if proxy else self.account_name,
            mode=WitnessesDataRetrieval.DEFAULT_MODE,
            witness_name_pattern=None,
            search_by_name_limit=WitnessesDataRetrieval.DEFAULT_SEARCH_BY_NAME_LIMIT,
        )
        witnesses_data: WitnessesData = wrapper.result_or_raise

        table = Table(title=f"Witnesses and votes of `{self.account_name}` account")

        table.add_column("voted", justify="left", style="cyan", no_wrap=True)
        table.add_column("rank", justify="right", style="green", no_wrap=True)
        table.add_column("witness name", justify="right", style="green", no_wrap=True)
        table.add_column("votes", justify="right", style="green", no_wrap=True)
        table.add_column("url", justify="right", style="green", no_wrap=True)
        table.add_column("created", justify="right", style="green", no_wrap=True)
        table.add_column("missed blocks", justify="right", style="green", no_wrap=True)
        table.add_column("last block", justify="right", style="green", no_wrap=True)
        table.add_column("price feed", justify="right", style="green", no_wrap=True)
        table.add_column("version", justify="right", style="green", no_wrap=True)

        witness_data: WitnessData
        for witness_data in witnesses_data.witnesses.values():
            table.add_row(
                f"{witness_data.voted}",
                f"{witness_data.rank}",
                f"{witness_data.name}",
                f"{witness_data.votes}",
                f"{witness_data.url}",
                f"{witness_data.created}",
                f"{witness_data.missed_blocks}",
                f"{witness_data.last_block}",
                f"{witness_data.price_feed}",
                f"{witness_data.version}",
            )
        console = Console()
        console.print(table)
