from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli
from clive.__private.cli.table_pagination_info import add_pagination_info_to_table_if_needed
from clive.__private.core.formatters.humanize import humanize_bool

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.proposals_data import (
        Proposal,
        ProposalsData,
        ProposalsDataRetrieval,
    )


@dataclass(kw_only=True)
class ShowProposals(WorldBasedCommand):
    account_name: str
    order_by: ProposalsDataRetrieval.Orders
    order_direction: ProposalsDataRetrieval.OrderDirections
    status: ProposalsDataRetrieval.Statuses
    page_size: int
    page_no: int

    async def _run(self) -> None:
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise
        proxy = accounts[0].proxy

        wrapper = await self.world.commands.retrieve_proposals_data(
            account_name=proxy if proxy else self.account_name,
            order=self.order_by,
            order_direction=self.order_direction,
            status=self.status,
        )
        proposals_data: ProposalsData = wrapper.result_or_raise
        start_index: int = self.page_no * self.page_size
        end_index: int = start_index + self.page_size
        proposals_chunk: list[Proposal] = proposals_data.proposals[start_index:end_index]

        proxy_name_message = f"`{self.account_name}`"
        if proxy:
            proxy_name_message += f" (proxy set to `{proxy}`)"
        table = Table(title=f"Proposals and votes of {proxy_name_message} account")

        table.add_column("voted", justify="left", style="cyan")
        table.add_column("title", justify="left", style="green", overflow="fold", min_width=20)
        table.add_column("id", justify="right", style="green")
        table.add_column("votes", justify="right", style="green", no_wrap=True)
        table.add_column("daily pay", justify="right", style="green", overflow="fold")
        table.add_column("start date", justify="right", style="green")
        table.add_column("end date", justify="right", style="green")

        proposal: Proposal
        for proposal in proposals_chunk:
            table.add_row(
                humanize_bool(proposal.voted),
                f"{proposal.title}",
                f"{proposal.proposal_id}",
                f"{proposal.votes}",
                f"{proposal.daily_pay} HBD",
                f"{proposal.pretty_start_date}",
                f"{proposal.pretty_end_date}",
            )

        add_pagination_info_to_table_if_needed(
            table=table, page_no=self.page_no, page_size=self.page_size, all_entries=len(proposals_data.proposals)
        )

        print_cli(table)
