from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from textual import work
from textual.reactive import var

from clive.__private.config import settings
from clive.__private.core.calculate_hp_from_votes import calculate_hp_from_votes
from clive.__private.ui.widgets.clive_widget import CliveWidget


@dataclass(eq=False)
class Witness:
    name: str
    created: datetime = field(default_factory=lambda: datetime.fromtimestamp(0))
    voted: bool = False
    votes: str = "?"
    rank: int | None = None
    missed_blocks: int = 0
    last_block: int = 0
    price_feed: str = "?"
    custom: bool = False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Witness):
            return NotImplemented
        return self.name == other.name


@dataclass
class GovernanceData:
    witnesses: list[Witness] | None = None
    witnesses_names: list[str] | None = None


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
        self.interval = self.set_interval(settings.get("node.refresh_rate", 1.5), self._update_governance_data)  # type: ignore[arg-type]

    @work(name="governance data update worker")
    async def _update_governance_data(self) -> None:
        """Method fill witnesses GovernanceData by a list of witnesses, which user voted for and witnesses from top 100."""
        working_account_name = self.app.world.profile_data.working_account.name

        list_witnesses_votes_response = await self.app.world.node.api.database_api.list_witness_votes(
            start=(working_account_name, ""), limit=30, order="by_account_witness"
        )

        voted_witnesses = [
            Witness(witness_vote.witness, voted=True)
            for witness_vote in list_witnesses_votes_response.votes
            if witness_vote.account == working_account_name
        ]

        list_witnesses_response = await self.app.world.node.api.database_api.list_witnesses(
            start=(1000000000000000000, ""), limit=200, order="by_vote_name"
        )

        gdpo = await self.app.world.app_state.get_dynamic_global_properties()

        top_200_witnesses = [
            Witness(
                witness.owner,
                created=witness.created,
                rank=rank,
                votes=calculate_hp_from_votes(witness.votes, gdpo.total_vesting_fund_hive, gdpo.total_vesting_shares),
                missed_blocks=witness.total_missed,
                voted=Witness(name=witness.owner) in voted_witnesses,
                last_block=witness.last_confirmed_block_num,
                price_feed=f"{int(witness.hbd_exchange_rate.base.amount) / 10 ** 3!s} $",
            )
            for rank, witness in enumerate(list_witnesses_response.witnesses, start=1)
        ]

        for witness in voted_witnesses:
            if witness in top_200_witnesses:
                voted_witnesses.remove(witness)
            else:
                top_200_witnesses.append(witness)

        witnesses_names = [witness.name for witness in top_200_witnesses]
        sorted_witnesses = sorted(top_200_witnesses, key=lambda witness: (not witness.voted, witness.rank))

        if self.content.witnesses_names != witnesses_names:
            self.content = GovernanceData(sorted_witnesses, witnesses_names)
