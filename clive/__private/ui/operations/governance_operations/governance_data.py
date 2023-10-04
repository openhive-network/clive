from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from textual import work
from textual.reactive import var

from clive.__private.config import settings
from clive.__private.core.formatters.humanize import humanize_hive_power
from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from clive.models import Asset


@dataclass
class Witness:
    name: str
    created: datetime = field(default_factory=lambda: datetime.fromtimestamp(0))
    voted: bool = False
    votes: str = "?"
    rank: int | None = None
    missed_blocks: int = 0
    last_block: int = 0
    price_feed: str = "?"
    version: str = ""
    url: str = ""


@dataclass
class GovernanceData:
    witnesses: dict[str, Witness] | None = None
    witnesses_names: list[str] | None = None
    number_of_votes: int = 0


class GovernanceDataProvider(CliveWidget):
    """
    A class for retrieving information about governance stored in a GovernanceData dataclass.

    To access the data after initializing the class, use the 'content' property.
    Management of governance data refreshing should be handled by a context manager, but also can be by stop_refreshing_data
    method.

    When the user decides to manually search for a witness by name, the refresh will stop and the list of witnesses searched will be posted in the
    witnesses field in the content var.
    """

    content: GovernanceData = var(GovernanceData())  # type: ignore[assignment]
    """It is used to check whether governance data has been refreshed and to store governance data."""

    def __init__(self) -> None:
        super().__init__()
        self._update_governance_data()
        self.interval = self.set_interval(settings.get("node.refresh_rate", 1.5), self._update_governance_data)

        self.__order_by_name: bool = False
        self.__witness_pattern: str = ""
        self.__limit: int = 150

    @work(name="governance data update worker")
    async def _update_governance_data(self) -> None:
        """
        Method fill witnesses GovernanceData by a list of witnesses, which user voted for and witnesses from top 150.

        If the user decides to search for a witness manually, only the witnesses searched will be filled in.

        """
        working_account_name = self.app.world.profile_data.working_account.name

        # This is due to receiving large json and counting aiohttp await response.json().
        # In future, the total timeout should be changed to modify the read timeout only.
        with self.app.world.modified_connection_details(timeout_secs=5):
            list_witnesses_votes_response = await self.app.world.node.api.database_api.list_witness_votes(
                start=(working_account_name, ""), limit=30, order="by_account_witness"
            )

            voted_witnesses = {
                witness_vote.witness: Witness(witness_vote.witness, voted=True)
                for witness_vote in list_witnesses_votes_response.votes
                if witness_vote.account == working_account_name
            }

            top_150_witnesses_response = await self.app.world.node.api.database_api.list_witnesses(
                start=(1000000000000000000, ""), limit=150, order="by_vote_name"
            )

            gdpo = await self.app.world.app_state.get_dynamic_global_properties()

        first_150_witnesses = {
            witness.owner: Witness(
                witness.owner,
                created=witness.created,
                rank=rank,
                votes=humanize_hive_power(
                    self.calculate_hp_from_votes(witness.votes, gdpo.total_vesting_fund_hive, gdpo.total_vesting_shares)
                ),
                missed_blocks=witness.total_missed,
                voted=witness.owner in voted_witnesses,
                last_block=witness.last_confirmed_block_num,
                price_feed=f"{int(witness.hbd_exchange_rate.base.amount) / 10 ** 3!s} $",
                version=witness.running_version,
                url=witness.url,
            )
            for rank, witness in enumerate(top_150_witnesses_response.witnesses, start=1)
        }

        for witness in voted_witnesses.items():
            if witness[0] not in first_150_witnesses.keys():
                first_150_witnesses[witness[0]] = witness[1]
                first_150_witnesses.popitem()

        number_of_votes = len(voted_witnesses)

        if self.order_by_name:
            with self.app.world.modified_connection_details(timeout_secs=5):
                list_witnesses_by_name = await self.app.world.node.api.database_api.list_witnesses(
                    start=self.witness_pattern_to_search, limit=self.limit, order="by_name"
                )

            searched_witnesses = {
                witness.owner: (
                    Witness(
                        witness.owner,
                        votes=humanize_hive_power(
                            self.calculate_hp_from_votes(
                                witness.votes, gdpo.total_vesting_fund_hive, gdpo.total_vesting_shares
                            )
                        ),
                        missed_blocks=witness.total_missed,
                        last_block=witness.last_confirmed_block_num,
                        price_feed=f"{int(witness.hbd_exchange_rate.base.amount) / 10 ** 3!s} $",
                        version=witness.running_version,
                        created=witness.created,
                        url=witness.url,
                    )
                    if witness.owner not in first_150_witnesses.keys()
                    else first_150_witnesses[witness.owner]
                )
                for witness in list_witnesses_by_name.witnesses
            }
            self.content = GovernanceData(searched_witnesses, number_of_votes=number_of_votes)  # type: ignore[arg-type]
        else:
            witnesses_names = [witness.name for witness in first_150_witnesses.values()]
            sorted_witnesses = dict(
                sorted(first_150_witnesses.items(), key=lambda witness: (not witness[1].voted, witness[1].rank))
            )

            if self.content.witnesses_names != witnesses_names or self.content.number_of_votes != number_of_votes:
                self.content = GovernanceData(sorted_witnesses, witnesses_names, number_of_votes)  # type: ignore[arg-type]

    def stop_refreshing_data(self) -> None:
        self.interval.stop()

    def pause_refreshing_data(self) -> None:
        self.interval.pause()

    def resume_refreshing_data(self) -> None:
        self.interval.resume()

    def calculate_hp_from_votes(
        self, votes: int, total_vesting_fund_hive: Asset.Hive, total_vesting_shares: Asset.Vests
    ) -> int:
        total_vesting_fund = int(total_vesting_fund_hive.amount) / 10**total_vesting_fund_hive.precision
        total_shares = int(total_vesting_shares.amount) / 10**total_vesting_shares.precision

        return (total_vesting_fund * (votes / total_shares)) // 1000000  # type: ignore[no-any-return]

    @property
    def order_by_name(self) -> bool:
        return self.__order_by_name

    @order_by_name.setter
    def order_by_name(self, value: bool) -> None:
        self.__order_by_name = value

    @property
    def witness_pattern_to_search(self) -> str:
        return self.__witness_pattern

    @witness_pattern_to_search.setter
    def witness_pattern_to_search(self, value: str | None) -> None:
        if value is None:
            self.__witness_pattern = ""
            return
        self.__witness_pattern = value
        self._update_governance_data()

    @property
    def limit(self) -> int:
        return self.__limit

    @limit.setter
    def limit(self, value: int | None) -> None:
        if value is None:
            self.__limit = 150
            return
        self.__limit = value
