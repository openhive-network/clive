from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.core.commands.data_retrieval.proposals_data import ProposalsDataRetrieval

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.proposals_data import Proposal, ProposalsData


@dataclass(kw_only=True)
class ShowProposals(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        if self.world.profile_data.working_account.name == self.account_name:
            proxy = self.world.profile_data.working_account.data.proxy
        else:
            core_account = await self.world.node.api.database_api.find_accounts(accounts=[self.account_name])
            proxy = core_account.proxy

        wrapper = await self.app.world.commands.retrieve_proposals_data(
            account_name=proxy if proxy else self.account_name,
            order=ProposalsDataRetrieval.DEFAULT_ORDER,
            order_direction=ProposalsDataRetrieval.DEFAULT_ORDER_DIRECTION,
            status=ProposalsDataRetrieval.DEFAULT_STATUS,
        )
        proposals_data: ProposalsData = wrapper.result_or_raise

        table = Table(title=f"Witnesses and votes of `{self.account_name}` account")

        table.add_column("voted", justify="left", style="cyan", no_wrap=True)
        table.add_column("title", justify="right", style="green", no_wrap=True)
        table.add_column("proposal id", justify="right", style="green", no_wrap=True)
        table.add_column("creator", justify="right", style="green", no_wrap=True)
        table.add_column("receiver", justify="right", style="green", no_wrap=True)
        table.add_column("votes", justify="right", style="green", no_wrap=True)
        table.add_column("daily pay", justify="right", style="green", no_wrap=True)
        table.add_column("status", justify="right", style="green", no_wrap=True)
        table.add_column("start date", justify="right", style="green", no_wrap=True)
        table.add_column("end date", justify="right", style="green", no_wrap=True)

        proposal: Proposal
        for proposal in proposals_data.proposals:
            table.add_row(
                f"{proposal.voted}",
                f"{proposal.title}",
                f"{proposal.proposal_id}",
                f"{proposal.creator}",
                f"{proposal.receiver}",
                f"{proposal.votes}",
                f"{proposal.daily_pay}",
                f"{proposal.status}",
                f"{proposal.start_date}",
                f"{proposal.end_date}",
            )
        console = Console()
        console.print(table)
