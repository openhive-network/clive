from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Literal

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
    list_150_witnesses: WitnessesList | None = None


@dataclass
class SanitizedData:
    gdpo: DynamicGlobalProperties
    witnesses_votes: dict[str, WitnessData]
    searched_150_witnesses: list[Witness]


@dataclass
class GovernanceData:
    witnesses: dict[str, WitnessData] = field(default_factory=dict)
    number_of_votes: int = 0

    @property
    def witness_names(self) -> list[str]:
        return list(self.witnesses.keys())


@dataclass(kw_only=True)
class GovernanceDataRetrieval(CommandDataRetrieval[HarvestedDataRaw, SanitizedData, GovernanceData]):
    node: Node
    account_name: str
    limit: int = 150
    mode: Literal["search_by_name", "search_top"] = "search_top"
    witness_name_pattern: str | None = None

    async def _harvest_data_from_api(self) -> HarvestedDataRaw:
        async with self.node.batch() as node:
            if self.mode == "search_top":
                return HarvestedDataRaw(
                    await node.api.database_api.get_dynamic_global_properties(),
                    await node.api.database_api.list_witness_votes(
                        start=(self.account_name, ""), limit=30, order="by_account_witness"
                    ),
                    await node.api.database_api.list_witnesses(
                        start=(1000000000000000000, ""), limit=self.limit, order="by_vote_name"
                    ),
                )
            return HarvestedDataRaw(
                await node.api.database_api.get_dynamic_global_properties(),
                await node.api.database_api.list_witness_votes(
                    start=(self.account_name, ""), limit=30, order="by_account_witness"
                ),
                await node.api.database_api.list_witnesses(
                    start=self.witness_name_pattern if self.witness_name_pattern is not None else "",
                    limit=self.limit,
                    order="by_name",
                ),
            )

    async def _sanitize_data(self, data: HarvestedDataRaw) -> SanitizedData:
        return SanitizedData(
            gdpo=self.__assert_gdpo(data.gdpo),
            witnesses_votes=self.__assert_witnesses_votes(data.list_witnesses_votes),
            searched_150_witnesses=self.__assert_list_150_witnesses(data.list_150_witnesses),
        )

    async def _process_data(self, data: SanitizedData) -> GovernanceData:
        """
        The function first checks if a witness from the api `list_witnesses` is in witnesses_votes - if so, set the voted parameter to True.

        If the witness voted for by the account is not in the `list_witnesses` response - remove the last witness in searched_witnesses and
        add the witness the account voted for to it.
        The witnesses that are returned are sorted first by the `voted` parameter and then by rank.
        """
        searched_witnesses = {
            witness.owner: WitnessData(
                witness.owner,
                created=witness.created,
                rank=rank if self.mode == "search_top" else None,
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
            for rank, witness in enumerate(data.searched_150_witnesses, start=1)
        }

        for witness in data.witnesses_votes.items():
            if witness[0] not in searched_witnesses.keys():
                searched_witnesses[witness[0]] = witness[1]  # type: ignore[index]
                searched_witnesses.popitem()

        sorted_witnesses = dict(
            sorted(searched_witnesses.items(), key=lambda witness: (not witness[1].voted, witness[1].rank))
        )

        return GovernanceData(witnesses=sorted_witnesses, number_of_votes=len(data.witnesses_votes))  # type: ignore[arg-type]

    def __assert_gdpo(self, data: DynamicGlobalProperties | None) -> DynamicGlobalProperties:
        assert data is not None, "DynamicGlobalProperties data is missing"
        return data

    def __assert_witnesses_votes(self, data: WitnessVotes | None) -> dict[str, WitnessData]:
        assert data is not None, "ListWitnessVotes data is missing"

        return {
            witness_vote.witness: WitnessData(name=witness_vote.witness, voted=True)
            for witness_vote in data.votes
            if witness_vote.account == self.account_name
        }

    def __assert_list_150_witnesses(self, data: WitnessesList | None) -> list[Witness]:
        assert data is not None, "ListWitnesses data is missing"
        return data.witnesses

    def calculate_hp_from_votes(
        self, votes: int, total_vesting_fund_hive: Asset.Hive, total_vesting_shares: Asset.Vests
    ) -> int:
        total_vesting_fund = int(total_vesting_fund_hive.amount) / 10**total_vesting_fund_hive.precision
        total_shares = int(total_vesting_shares.amount) / 10**total_vesting_shares.precision

        return (total_vesting_fund * (votes / total_shares)) // 1000000  # type: ignore[no-any-return]
