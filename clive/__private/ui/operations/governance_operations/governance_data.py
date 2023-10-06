from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from textual import work
from textual.reactive import var

from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from clive.models.aliased import WitnessesVotes, WitnessType


@dataclass
class GovernanceData:
    top_100_witnesses: list[WitnessType] | None = None
    voted_witnesses: list[WitnessesVotes] | None = None


class GovernanceDataProvider(CliveWidget):
    """A class for retrieving information about governance stored in a GovernanceData dataclass."""

    content: GovernanceData = var(GovernanceData())  # type: ignore[assignment]

    def __init__(self) -> None:
        super().__init__()
        self._update_governance_data()

    @work(name="governance data update worker")
    async def _update_governance_data(self) -> None:
        working_account_name = self.app.world.profile_data.working_account.name

        list_witnesses_response = await self.app.world.node.api.database_api.list_witnesses(
            start=(0, ""), limit=100, order="by_vote_name"
        )
        list_witnesses_votes_response = await self.app.world.node.api.database_api.list_witness_votes(
            start=(working_account_name, ""), limit=30, order="by_account_witness"
        )

        top_100_witnesses = list_witnesses_response.witnesses
        voted_witnesses = list_witnesses_votes_response.votes

        new_governance_data = GovernanceData(top_100_witnesses, voted_witnesses)
        self.content = new_governance_data
