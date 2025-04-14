from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Literal, TypeAliasType, get_args

from beekeepy.exceptions import UnknownDecisionPathError

from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.__private.core.formatters.humanize import humanize_datetime, humanize_votes_with_suffix
from clive.__private.models import Asset

if TYPE_CHECKING:
    import datetime

    from clive.__private.core.node import Node
    from clive.__private.models.schemas import DynamicGlobalProperties, ListProposals, ListProposalVotes
    from clive.__private.models.schemas import Proposal as SchemasProposal
    from wax.helpy import DatabaseApiCommons


@dataclass
class Proposal:
    title: str
    proposal_id: int
    creator: str
    receiver: str
    votes: str
    daily_pay: str
    status: str
    start_date: datetime.datetime
    end_date: datetime.datetime
    voted: bool = False

    @property
    def pretty_start_date(self) -> str:
        return humanize_datetime(self.start_date, with_time=False)

    @property
    def pretty_end_date(self) -> str:
        return humanize_datetime(self.end_date, with_time=False)


@dataclass
class HarvestedDataRaw:
    gdpo: DynamicGlobalProperties | None = None
    list_proposals: ListProposals | None = None
    list_voted_proposals: ListProposalVotes | None = None


@dataclass
class SanitizedData:
    gdpo: DynamicGlobalProperties
    list_proposals: list[SchemasProposal]
    list_voted_proposals: list[SchemasProposal]


@dataclass
class ProposalsData:
    proposals: list[Proposal]


_Orders = Literal["by_total_votes_with_voted_first", "by_total_votes", "by_start_date", "by_end_date", "by_creator"]
_OrderDirections = Literal["ascending", "descending"]
_Statuses = Literal["all", "active", "inactive", "votable", "expired"]


@dataclass(kw_only=True)
class ProposalsDataRetrieval(CommandDataRetrieval[HarvestedDataRaw, SanitizedData, ProposalsData]):
    Orders = TypeAliasType("Orders", _Orders)
    OrderDirections = TypeAliasType("OrderDirections", _OrderDirections)
    Statuses = TypeAliasType("Statuses", _Statuses)

    ORDERS: ClassVar[tuple[Orders, ...]] = get_args(_Orders)
    ORDER_DIRECTIONS: ClassVar[tuple[OrderDirections, ...]] = get_args(_OrderDirections)
    STATUSES: ClassVar[tuple[Statuses, ...]] = get_args(_Statuses)

    MAX_POSSIBLE_NUMBER_OF_VOTES: ClassVar[int] = 2**63 - 1
    MAX_SEARCHED_PROPOSALS_HARD_LIMIT: ClassVar[int] = 100
    DEFAULT_STATUS: ClassVar[Statuses] = "votable"
    DEFAULT_ORDER: ClassVar[Orders] = "by_total_votes_with_voted_first"
    DEFAULT_ORDER_DIRECTION: ClassVar[OrderDirections] = "descending"

    node: Node
    account_name: str
    order: Orders = DEFAULT_ORDER
    order_direction: OrderDirections = DEFAULT_ORDER_DIRECTION
    status: Statuses = DEFAULT_STATUS

    async def _harvest_data_from_api(self) -> HarvestedDataRaw:
        async with await self.node.batch() as node:
            gdpo = await node.api.database_api.get_dynamic_global_properties()
            proposal_votes = await node.api.database_api.list_proposal_votes(
                start=[self.account_name],
                limit=self.MAX_SEARCHED_PROPOSALS_HARD_LIMIT,
                order="by_voter_proposal",
                order_direction=self.order_direction,
                status=self.status,
            )

            order: DatabaseApiCommons.SORT_TYPES
            if self.order == "by_total_votes_with_voted_first":
                order = "by_total_votes"
            elif self.order in self.ORDERS:
                order = self.order
            else:
                raise ValueError(f"Unknown order: {self.order}")

            searched_proposals = await node.api.database_api.list_proposals(
                start=[],
                limit=self.MAX_SEARCHED_PROPOSALS_HARD_LIMIT,
                order=order,
                order_direction=self.order_direction,
                status=self.status,
            )
            return HarvestedDataRaw(gdpo, searched_proposals, proposal_votes)
        raise UnknownDecisionPathError(f"{self.__class__.__name__}:_harvest_data_from_api")

    async def _sanitize_data(self, data: HarvestedDataRaw) -> SanitizedData:
        return SanitizedData(
            gdpo=self.__assert_gdpo(data.gdpo),
            list_proposals=self.__assert_proposals_list(data.list_proposals),
            list_voted_proposals=self.__assert_proposals_votes(data.list_voted_proposals),
        )

    async def _process_data(self, data: SanitizedData) -> ProposalsData:
        if self.order == "by_total_votes_with_voted_first":
            return ProposalsData(self.__get_top_proposals_with_voted_first(data))
        return ProposalsData(
            proposals=self.__get_prepared_proposals(data.list_proposals, data),
        )

    def __create_proposal_data(self, proposal: SchemasProposal, data: SanitizedData) -> Proposal:
        return Proposal(
            title=proposal.subject,
            proposal_id=proposal.proposal_id,
            creator=proposal.creator,
            receiver=proposal.receiver,
            daily_pay=Asset.pretty_amount(proposal.daily_pay),
            votes=humanize_votes_with_suffix(proposal.total_votes, data.gdpo),
            status=proposal.status,
            start_date=proposal.start_date,
            end_date=proposal.end_date,
            voted=proposal in data.list_voted_proposals,
        )

    def __get_top_proposals_with_voted_first(self, data: SanitizedData) -> list[Proposal]:
        voted_proposals = self.__get_prepared_proposals(data.list_voted_proposals, data)
        top_proposals = self.__get_prepared_proposals(data.list_proposals, data)

        combined_proposals: list[Proposal] = top_proposals

        for proposal in combined_proposals:
            if proposal in voted_proposals:
                proposal.voted = True
                voted_proposals.remove(proposal)

        combined_proposals.extend(voted_proposals)

        return sorted(combined_proposals, key=lambda proposal: not proposal.voted)

    def __get_prepared_proposals(self, proposals: list[SchemasProposal], data: SanitizedData) -> list[Proposal]:
        return [self.__create_proposal_data(proposal, data) for proposal in proposals]

    def __get_proposals_ids(self, proposals: list[SchemasProposal]) -> list[int]:
        return [proposal.proposal_id for proposal in proposals]

    def __assert_gdpo(self, data: DynamicGlobalProperties | None) -> DynamicGlobalProperties:
        assert data is not None, "DynamicGlobalProperties data is missing"
        return data

    def __assert_proposals_list(self, data: ListProposals | None) -> list[SchemasProposal]:
        assert data is not None, "ListProposals data is missing"
        return data.proposals

    def __assert_proposals_votes(self, data: ListProposalVotes | None) -> list[SchemasProposal]:
        assert data is not None, "ListProposalsVotes data is missing"
        return [
            proposal_vote.proposal for proposal_vote in data.proposal_votes if proposal_vote.voter == self.account_name
        ]
