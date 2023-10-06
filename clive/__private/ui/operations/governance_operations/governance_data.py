from __future__ import annotations

from dataclasses import dataclass

from textual import work
from textual.reactive import var

from clive.__private.ui.widgets.clive_widget import CliveWidget


@dataclass(eq=False)
class Witness:
    name: str
    voted: bool = False
    votes: int = 0
    rank: int | None = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Witness):
            return NotImplemented
        return self.name == other.name


@dataclass
class GovernanceData:
    witnesses: list[Witness] | None = None


class GovernanceDataProvider(CliveWidget):
    """
    A class for retrieving information about governance stored in a GovernanceData dataclass.

    To access the data after initializing the class, use the 'content' property.
    Management of governance data refreshing should be handled by a context manager.
    """

    content: GovernanceData = var(GovernanceData())  # type: ignore[assignment]
    """It is used to check whether governance data has been refreshed and to store governance data."""

    def __init__(self) -> None:
        super().__init__()
        self._update_governance_data()

    @work(name="governance data update worker")
    async def _update_governance_data(self) -> None:
        """Method fill witnesses GovernanceData by a list of witnesses, which user voted for and witnesses from top 100."""
        working_account_name = self.app.world.profile_data.working_account.name

        list_witnesses_response = await self.app.world.node.api.database_api.list_witnesses(
            start=(0, ""), limit=105, order="by_vote_name"
        )

        list_witnesses_votes_response = await self.app.world.node.api.database_api.list_witness_votes(
            start=(working_account_name, ""), limit=30, order="by_account_witness"
        )

        top_100_witnesses = [
            Witness(witness.owner, rank=rank, votes=witness.votes)
            for rank, witness in enumerate(list_witnesses_response.witnesses, start=1)
        ]
        voted_witnesses = [
            Witness(witness_vote.witness)
            for witness_vote in list_witnesses_votes_response.votes
            if witness_vote.account == working_account_name
        ]

        for witness in top_100_witnesses:
            if witness in voted_witnesses:
                witness.voted = True

        sorted_witnesses = sorted(top_100_witnesses, key=lambda witness: (witness.voted, witness.rank))

        new_governance_data = GovernanceData(sorted_witnesses)
        self.content = new_governance_data
