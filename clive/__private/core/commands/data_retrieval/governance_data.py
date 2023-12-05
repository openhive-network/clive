from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, ClassVar, Literal

from clive.__private.core.commands.abc.command_data_retrieval import (
    CommandDataRetrieval,
)
from clive.__private.core.formatters.humanize import humanize_hive_power

if TYPE_CHECKING:
    from clive.__private.core.node import Node
    from clive.models import Asset
    from clive.models.aliased import DynamicGlobalProperties, Witness, WitnessesList, WitnessVotes


@dataclass
class WitnessData:
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
class HarvestedDataRaw:
    gdpo: DynamicGlobalProperties | None = None
    list_witnesses_votes: WitnessVotes | None = None
    top_150_witnesses: WitnessesList | None = None
    witnesses_searched_by_name: WitnessesList | None = None


@dataclass
class SanitizedData:
    gdpo: DynamicGlobalProperties
    witnesses_votes: list[str]
    top_150_witnesses: list[Witness]
    witnesses_searched_by_name: list[Witness] | None
    """Could be None, as there is no need to download it when the order is by votes."""


@dataclass
class GovernanceData:
    witnesses: dict[str, WitnessData] = field(default_factory=dict)
    number_of_votes: int = 0

    @property
    def witness_names(self) -> list[str]:
        return list(self.witnesses.keys())


@dataclass(kw_only=True)
class GovernanceDataRetrieval(CommandDataRetrieval[HarvestedDataRaw, SanitizedData, GovernanceData]):
    MAX_POSSIBLE_NUMBER_OF_VOTES: ClassVar[int] = 2**63 - 1
    DEFAULT_LIMIT: ClassVar[int] = 150
    DEFAULT_MODE: ClassVar[Literal["search_top"]] = "search_top"

    node: Node
    account_name: str
    limit: int = DEFAULT_LIMIT
    mode: Literal["search_by_name", "search_top"] = DEFAULT_MODE
    witness_name_pattern: str | None = None

    async def _harvest_data_from_api(self) -> HarvestedDataRaw:
        # This is due to receiving large json and counting aiohttp await response.json().
        # In future, the total timeout should be changed to modify the read timeout only.
        with self.node.modified_connection_details(timeout_secs=6):
            async with self.node.batch() as node:
                gdpo = await node.api.database_api.get_dynamic_global_properties()

                witness_votes = await node.api.database_api.list_witness_votes(
                    start=(self.account_name, ""), limit=30, order="by_account_witness"
                )

                top_witnesses = await node.api.database_api.list_witnesses(
                    start=(self.MAX_POSSIBLE_NUMBER_OF_VOTES, ""), limit=self.limit, order="by_vote_name"
                )

                witnesses_by_name: WitnessesList | None = None

                if self.mode == "search_by_name":
                    witnesses_by_name = await node.api.database_api.list_witnesses(
                        start=self.witness_name_pattern if self.witness_name_pattern is not None else "",
                        limit=self.limit,
                        order="by_name",
                    )

                return HarvestedDataRaw(gdpo, witness_votes, top_witnesses, witnesses_by_name)

    async def _sanitize_data(self, data: HarvestedDataRaw) -> SanitizedData:
        in_search_by_name_mode = self.mode == "search_by_name"
        return SanitizedData(
            gdpo=self.__assert_gdpo(data.gdpo),
            witnesses_votes=self.__assert_witnesses_votes(data.list_witnesses_votes),
            top_150_witnesses=self.__assert_list_witnesses(data.top_150_witnesses),
            witnesses_searched_by_name=(
                self.__assert_list_witnesses(data.witnesses_searched_by_name) if in_search_by_name_mode else None
            ),
        )

    async def _process_data(self, data: SanitizedData) -> GovernanceData:
        """
        The function first checks if a witness from the api `list_witnesses` is in witnesses_votes - if so, set the voted parameter to True.

        If the witness voted for by the account is not in the `list_witnesses` response - remove the last witness in searched_witnesses and
        add the witness the account voted for to it.
        If the user wants to order by_name, the function returns a list of searched witnesses by_name with the information
        retrieved about ranks from the top_150_witnesses response.
        The witnesses that are returned are sorted first by the `voted` parameter and then by rank.
        """

        def create_witness_data(witness: Witness, rank: int | None = None) -> WitnessData:
            return WitnessData(
                witness.owner,
                created=witness.created,
                rank=rank,
                votes=humanize_hive_power(
                    self.calculate_hp_from_votes(
                        witness.votes, data.gdpo.total_vesting_fund_hive, data.gdpo.total_vesting_shares
                    )
                ),
                missed_blocks=witness.total_missed,
                voted=witness.owner in data.witnesses_votes,
                last_block=witness.last_confirmed_block_num,
                price_feed=f"{int(witness.hbd_exchange_rate.base.amount) / 10 ** 3!s} $",
                version=witness.running_version,
                url=witness.url,
            )

        top_150_witnesses: dict[str, WitnessData] = {
            witness.owner: create_witness_data(witness, rank)
            for rank, witness in enumerate(data.top_150_witnesses, start=1)
        }

        # Include witnesses that account voted for but are not included in the top
        voted_but_not_in_top_witnesses: dict[str, WitnessData] = {
            witness_name: WitnessData(witness_name, voted=True)
            for witness_name in data.witnesses_votes
            if witness_name not in top_150_witnesses
        }

        for _ in voted_but_not_in_top_witnesses:
            top_150_witnesses.popitem()

        top_150_witnesses.update(voted_but_not_in_top_witnesses)

        # Sort the witnesses based on voted status and rank
        sorted_witnesses = OrderedDict(
            sorted(top_150_witnesses.items(), key=lambda witness: (not witness[1].voted, witness[1].rank))
        )

        if self.mode == "search_by_name":
            assert data.witnesses_searched_by_name is not None, "Witnesses searched by name are missing"

            searched_witnesses_by_name: OrderedDict[str, WitnessData] = OrderedDict(
                {
                    witness.owner: (
                        create_witness_data(witness)
                        if witness.owner not in top_150_witnesses.keys()
                        else top_150_witnesses[witness.owner]
                    )
                    for witness in data.witnesses_searched_by_name
                }
            )
            sorted_witnesses = searched_witnesses_by_name  # they are already sorted by_name

        assert len(sorted_witnesses) == self.limit

        return GovernanceData(witnesses=sorted_witnesses, number_of_votes=len(data.witnesses_votes))

    def __assert_gdpo(self, data: DynamicGlobalProperties | None) -> DynamicGlobalProperties:
        assert data is not None, "DynamicGlobalProperties data is missing"
        return data

    def __assert_witnesses_votes(self, data: WitnessVotes | None) -> list[str]:
        assert data is not None, "ListWitnessVotes data is missing"
        return [witness_vote.witness for witness_vote in data.votes if witness_vote.account == self.account_name]

    def __assert_list_witnesses(self, data: WitnessesList | None) -> list[Witness]:
        assert data is not None, "ListWitnesses data is missing"
        return data.witnesses

    def calculate_hp_from_votes(
        self, votes: int, total_vesting_fund_hive: Asset.Hive, total_vesting_shares: Asset.Vests
    ) -> int:
        total_vesting_fund = int(total_vesting_fund_hive.amount) / 10**total_vesting_fund_hive.precision
        total_shares = int(total_vesting_shares.amount) / 10**total_vesting_shares.precision

        return (total_vesting_fund * (votes / total_shares)) // 1000000  # type: ignore[no-any-return]
