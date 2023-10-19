from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from textual import work
from textual.reactive import var

from clive.__private.core.calculate_hp_from_votes import calculate_hp_from_votes
from clive.__private.ui.widgets.clive_widget import CliveWidget


@dataclass(eq=False)
class Witness:
    name: str
    created: datetime = field(default_factory=lambda: datetime.fromtimestamp(0))
    voted: bool = False
    votes: str = "0 HP"
    rank: int | None = None
    missed_blocks: int = 0

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
            start=(0, ""), limit=150, order="by_vote_name"
        )

        list_witnesses_votes_response = await self.app.world.node.api.database_api.list_witness_votes(
            start=(working_account_name, ""), limit=30, order="by_account_witness"
        )

        gdpo = await self.app.world.app_state.get_dynamic_global_properties()

        top_150_witnesses = [
            Witness(
                witness.owner,
                created=witness.created,
                rank=rank,
                votes=calculate_hp_from_votes(witness.votes, gdpo.total_vesting_fund_hive, gdpo.total_vesting_shares),
                missed_blocks=witness.total_missed,
            )
            for rank, witness in enumerate(list_witnesses_response.witnesses, start=1)
        ]
        voted_witnesses = [
            Witness(witness_vote.witness, voted=True)
            for witness_vote in list_witnesses_votes_response.votes
            if witness_vote.account == working_account_name
        ]

        for witness in top_150_witnesses:
            if witness in voted_witnesses:
                voted_witnesses.remove(witness)
                witness.voted = True

        top_150_witnesses.extend(voted_witnesses)
        sorted_witnesses = sorted(top_150_witnesses, key=lambda witness: (witness.voted, witness.rank))

        new_governance_data = GovernanceData(sorted_witnesses)
        self.content = new_governance_data
