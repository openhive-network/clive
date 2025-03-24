from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar, Literal

from beekeepy.exceptions import UnknownDecisionPathError
from typing_extensions import TypeAliasType

from clive.__private.core.commands.abc.command_data_retrieval import (
    CommandDataRetrieval,
)
from clive.__private.core.date_utils import utc_epoch
from clive.__private.core.formatters.humanize import (
    humanize_datetime,
    humanize_hbd_exchange_rate,
    humanize_votes_with_suffix,
)

if TYPE_CHECKING:
    from datetime import datetime

    from clive.__private.core.node import Node
    from clive.__private.models.schemas import DynamicGlobalProperties, ListWitnesses, ListWitnessVotes, Witness


@dataclass
class WitnessData:
    name: str
    created: datetime = field(default_factory=utc_epoch)
    voted: bool = False
    votes: str = "?"
    rank: int | None = None
    missed_blocks: int = 0
    last_block: int = 0
    price_feed: str = "?"
    version: str = "?"
    url: str = "?"

    @property
    def pretty_created(self) -> str:
        return humanize_datetime(self.created, with_time=False)


@dataclass
class HarvestedDataRaw:
    gdpo: DynamicGlobalProperties | None = None
    list_witnesses_votes: ListWitnessVotes | None = None
    top_witnesses: ListWitnesses | None = None
    witnesses_searched_by_name: ListWitnesses | None = None


@dataclass
class SanitizedData:
    gdpo: DynamicGlobalProperties
    witnesses_votes: list[str]
    top_witnesses: list[Witness]
    witnesses_searched_by_name: list[Witness] | None
    """Could be None, as there is no need to download it when the order is by votes."""


@dataclass
class WitnessesData:
    witnesses: dict[str, WitnessData]
    number_of_votes: int

    @property
    def witness_names(self) -> list[str]:
        return list(self.witnesses.keys())


@dataclass(kw_only=True)
class WitnessesDataRetrieval(CommandDataRetrieval[HarvestedDataRaw, SanitizedData, WitnessesData]):
    Modes = TypeAliasType("Modes", Literal["search_by_pattern", "search_top_with_voted_first"])
    """
    Available modes for retrieving witnesses data.

    search_by_pattern:
    ------------------
    Retrieves witnesses by name pattern. The list is sorted the same way as it comes from list_witnesses (sort by_name)
    call.
    Amount of witnesses is limited to the search_by_name_limit.

    search_top_with_voted_first:
    ------------------------------
    Retrieves top witnesses with the ones voted for by the account.
    The list is sorted by the voted status and then by rank.
    Amount of witnesses is limited to the TOP_WITNESSES_HARD_LIMIT.
    """

    MAX_POSSIBLE_NUMBER_OF_VOTES: ClassVar[int] = 2**63 - 1
    MAX_POSSIBLE_NUMBER_OF_WITNESSES_VOTED_FOR: ClassVar[int] = 30

    TOP_WITNESSES_HARD_LIMIT: ClassVar[int] = 150

    DEFAULT_SEARCH_BY_NAME_LIMIT: ClassVar[int] = 50
    DEFAULT_MODE: ClassVar[Modes] = "search_top_with_voted_first"

    node: Node
    account_name: str
    mode: Modes = DEFAULT_MODE
    witness_name_pattern: str | None = None
    """Required only if mode is set to search_by_pattern."""
    search_by_pattern_limit: int = DEFAULT_SEARCH_BY_NAME_LIMIT
    """Doesn't matter if mode is different than search_by_pattern."""

    async def _harvest_data_from_api(self) -> HarvestedDataRaw:
        async with await self.node.batch() as node:
            gdpo = await node.api.database_api.get_dynamic_global_properties()

            witness_votes = await node.api.database_api.list_witness_votes(
                start=(self.account_name, ""),
                limit=self.MAX_POSSIBLE_NUMBER_OF_WITNESSES_VOTED_FOR,
                order="by_account_witness",
            )

            top_witnesses = await node.api.database_api.list_witnesses(
                start=(self.MAX_POSSIBLE_NUMBER_OF_VOTES, ""),
                limit=self.TOP_WITNESSES_HARD_LIMIT,
                order="by_vote_name",
            )

            witnesses_by_name: ListWitnesses | None = None

            if self.mode == "search_by_pattern":
                witnesses_by_name = await node.api.database_api.list_witnesses(
                    start=self.witness_name_pattern if self.witness_name_pattern is not None else "",
                    limit=self.search_by_pattern_limit,
                    order="by_name",
                )

            return HarvestedDataRaw(gdpo, witness_votes, top_witnesses, witnesses_by_name)
        raise UnknownDecisionPathError(f"{self.__class__.__name__}:_harvest_data_from_api")

    async def _sanitize_data(self, data: HarvestedDataRaw) -> SanitizedData:
        in_search_by_name_mode = self.mode == "search_by_pattern"
        return SanitizedData(
            gdpo=self.__assert_gdpo(data.gdpo),
            witnesses_votes=self.__assert_witnesses_votes(data.list_witnesses_votes),
            top_witnesses=self.__assert_list_witnesses(data.top_witnesses),
            witnesses_searched_by_name=(
                self.__assert_list_witnesses(data.witnesses_searched_by_name) if in_search_by_name_mode else None
            ),
        )

    async def _process_data(self, data: SanitizedData) -> WitnessesData:
        if self.mode == "search_top_with_voted_first":
            witnesses = self.__get_top_witnesses_with_voted_first(data)
        elif self.mode == "search_by_pattern":
            witnesses = self.__get_witnesses_by_pattern(data)
        else:
            raise NotImplementedError(f"Unknown mode: {self.mode}")

        return WitnessesData(witnesses=witnesses, number_of_votes=len(data.witnesses_votes))

    def __get_top_witnesses(self, data: SanitizedData) -> OrderedDict[str, WitnessData]:
        return OrderedDict(
            {
                witness.owner: self.__create_witness_data(witness, data, rank=rank)
                for rank, witness in enumerate(data.top_witnesses, start=1)
            }
        )

    def __get_top_witnesses_with_voted_first(self, data: SanitizedData) -> OrderedDict[str, WitnessData]:
        top_witnesses = self.__get_top_witnesses(data)

        # Include witnesses that account voted for but are not included in the top
        voted_but_not_in_top_witnesses: dict[str, WitnessData] = {
            witness_name: WitnessData(witness_name, voted=True)
            for witness_name in data.witnesses_votes
            if witness_name not in top_witnesses
        }

        for _ in voted_but_not_in_top_witnesses:
            top_witnesses.popitem()

        top_witnesses_with_all_voted_for = voted_but_not_in_top_witnesses | top_witnesses

        # Sort the witnesses based on voted status and rank
        return OrderedDict(
            sorted(
                top_witnesses_with_all_voted_for.items(), key=lambda witness: (not witness[1].voted, witness[1].rank)
            )
        )

    def __get_witnesses_by_pattern(self, data: SanitizedData) -> OrderedDict[str, WitnessData]:
        assert data.witnesses_searched_by_name is not None, "Witnesses searched by name are missing"

        # Get the processed list of top witnesses because it is needed to get the rank of the searched witnesses
        top_witnesses = self.__get_top_witnesses(data)

        witnesses: OrderedDict[str, WitnessData] = OrderedDict()
        for witness in data.witnesses_searched_by_name:
            if witness.owner in top_witnesses:
                witness_data = top_witnesses[witness.owner]
            else:
                witness_data = self.__create_witness_data(witness, data)
            witnesses[witness.owner] = witness_data

        return witnesses

    def __create_witness_data(self, witness: Witness, data: SanitizedData, *, rank: int | None = None) -> WitnessData:
        return WitnessData(
            witness.owner,
            created=witness.created.value,
            rank=rank,
            votes=humanize_votes_with_suffix(witness.votes.value, data.gdpo),
            missed_blocks=witness.total_missed.value,
            voted=witness.owner in data.witnesses_votes,
            last_block=witness.last_confirmed_block_num.value,
            price_feed=humanize_hbd_exchange_rate(witness.hbd_exchange_rate),
            version=witness.running_version,
            url=witness.url,
        )

    def __assert_gdpo(self, data: DynamicGlobalProperties | None) -> DynamicGlobalProperties:
        assert data is not None, "DynamicGlobalProperties data is missing"
        return data

    def __assert_witnesses_votes(self, data: ListWitnessVotes | None) -> list[str]:
        assert data is not None, "ListWitnessVotes data is missing"
        return [witness_vote.witness for witness_vote in data.votes if witness_vote.account == self.account_name]

    def __assert_list_witnesses(self, data: ListWitnesses | None) -> list[Witness]:
        assert data is not None, "ListWitnesses data is missing"
        return data.witnesses
