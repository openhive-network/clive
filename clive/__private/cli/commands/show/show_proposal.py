from __future__ import annotations

from dataclasses import dataclass

from rich.console import Console
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.core.formatters.humanize import humanize_datetime, humanize_votes_with_comma
from clive.__private.models import Asset


@dataclass(kw_only=True)
class ShowProposal(WorldBasedCommand):
    """
    Show the details of a proposal by its ID.

    Args:
        proposal_id: The ID of the proposal to show.
    """

    proposal_id: int

    async def _run(self) -> None:
        """
        Show the details of a proposal by its ID.

        This method retrieves the proposal details from the world commands and formats
        them into a readable table format using Rich. It includes information such as
        proposal ID, creator, receiver, start date, end date, daily pay, subject,
        permlink, total votes, and status.

        Returns:
            None: The method prints the proposal details table into the console.
        """
        wrapper = await self.world.commands.find_proposal(proposal_id=self.proposal_id)
        proposal = wrapper.result_or_raise

        gdpo = await self.world.node.api.database_api.get_dynamic_global_properties()
        votes = humanize_votes_with_comma(proposal.total_votes, gdpo)
        daily_pay = Asset.pretty_amount(proposal.daily_pay)

        table = Table(title=f"Details of proposal with id `{self.proposal_id}`", show_header=False)

        table.add_row("proposal id", f"{proposal.proposal_id}")
        table.add_row("creator", f"{proposal.creator}")
        table.add_row("receiver", f"{proposal.receiver}")
        table.add_row("start date", f"{humanize_datetime(proposal.start_date, with_time=False)}")
        table.add_row("end date", f"{humanize_datetime(proposal.end_date, with_time=False)}")
        table.add_row("daily pay", f"{daily_pay} HBD")
        table.add_row("subject", f"{proposal.subject}")
        table.add_row("permlink", f"{proposal.permlink}")
        table.add_row("total votes", f"{votes}")
        table.add_row("status", f"{proposal.status}")

        console = Console()
        console.print(table)
