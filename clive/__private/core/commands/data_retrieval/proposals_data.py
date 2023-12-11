from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar, Literal, TypeAlias

from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.__private.core.formatters.humanize import humanize_hive_power
from clive.models import Asset

if TYPE_CHECKING:
    from clive.__private.core.node import Node
    from clive.models.aliased import DynamicGlobalProperties, ProposalSchema, ProposalsList, ProposalVotes


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


@dataclass
class HarvestedDataRaw:
    gdpo: DynamicGlobalProperties | None = None
    list_proposals: ProposalsList | None = None
    list_voted_proposals: ProposalVotes | None = None


@dataclass
class SanitizedData:
    gdpo: DynamicGlobalProperties
    list_proposals: list[ProposalSchema]
    list_voted_proposals: list[ProposalSchema]


@dataclass
class ProposalsData:
    proposals: list[Proposal] = field(default_factory=list)
    voted_proposals_ids: list[int] = field(default_factory=list)


@dataclass(kw_only=True)
class ProposalsDataRetrieval(CommandDataRetrieval[HarvestedDataRaw, SanitizedData, ProposalsData]):
    Modes: ClassVar[TypeAlias] = Literal[
        "my_votes_first", "search_by_total_votes", "search_by_start_date", "search_by_end_date", "search_by_creator"
    ]
    """
    Amount of proposals is limited to the MAX_SEARCHED_PROPOSALS_HARD_LIMIT.

    Available modes for retrieving proposals data.

    my_votes_first:
    ------------------
    Retrieves top proposals with the ones voted for by the account.
    The list is sorted by the unvoted status and then by votes.

    search_by_total_votes:
    ------------------
    Retrieves top proposals.
    The list is sorted by votes.

    search_by_start_date:
    ------------------------------
    Retrieves proposals sorted by start date.
    The list is sorted just by start date, ascending or descending which user choose by order_direction.

    search_by_end_date:
    ------------------------------
    Retrieves proposals sorted by ebd date.
    The list is sorted just by end date, ascending or descending which user choose by order_direction.

    search_by_creator:
    ------------------------------
    Retrieves proposals sorted by creator.
    The list is sorted just by creator, ascending or descending which user choose by order_direction.
    """
    OrderDirections: ClassVar[TypeAlias] = Literal["ascending", "descending"]
    ProposalStatus: ClassVar[TypeAlias] = Literal["all", "active", "inactive", "votable", "expired", "inactive"]

    MAX_POSSIBLE_NUMBER_OF_VOTES: ClassVar[int] = 2**63 - 1
    MAX_SEARCHED_PROPOSALS_HARD_LIMIT: ClassVar[int] = 100
    DEFAULT_STATUS: ClassVar[ProposalStatus] = "active"
    DEFAULT_MODE: ClassVar[Modes] = "search_by_total_votes"
    DEFAULT_ORDER_DIRECTION: ClassVar[OrderDirections] = "descending"

    node: Node
    account_name: str
    mode: Modes = DEFAULT_MODE
    order_direction: OrderDirections = DEFAULT_ORDER_DIRECTION
    status: ProposalStatus = DEFAULT_STATUS

    async def _harvest_data_from_api(self) -> HarvestedDataRaw:
        with self.node.modified_connection_details(timeout_secs=6):
            async with self.node.batch() as node:
                gdpo = await node.api.database_api.get_dynamic_global_properties()
                proposal_votes = await node.api.database_api.list_proposal_votes(
                    start=[self.account_name],
                    limit=self.MAX_SEARCHED_PROPOSALS_HARD_LIMIT,
                    order="by_voter_proposal",
                    order_direction=self.order_direction,
                    status=self.status,
                )

                if self.mode == "my_votes_first" or self.mode == "search_by_total_votes":
                    searched_proposals = await node.api.database_api.list_proposals(
                        start=[self.MAX_POSSIBLE_NUMBER_OF_VOTES] if self.order_direction == "descending" else [0],
                        limit=self.MAX_SEARCHED_PROPOSALS_HARD_LIMIT,
                        order="by_total_votes",
                        order_direction=self.order_direction,
                        status=self.status,
                    )
                    return HarvestedDataRaw(gdpo, searched_proposals, proposal_votes)

                if self.mode == "search_by_start_date":
                    searched_proposals = await node.api.database_api.list_proposals(
                        start=(
                            [self.__get_today_datetime() - datetime.timedelta(2500)]
                            if self.order_direction == "ascending"
                            else [self.__get_today_datetime()]
                        ),
                        limit=self.MAX_SEARCHED_PROPOSALS_HARD_LIMIT,
                        order="by_start_date",
                        order_direction=self.order_direction,
                        status=self.status,
                    )
                    return HarvestedDataRaw(gdpo, searched_proposals, proposal_votes)

                if self.mode == "search_by_end_date":
                    searched_proposals = await node.api.database_api.list_proposals(
                        start=(
                            [self.__get_today_datetime() - datetime.timedelta(2500)]
                            if self.order_direction == "ascending"
                            else [self.__get_today_datetime() + datetime.timedelta(2500)]
                        ),
                        limit=self.MAX_SEARCHED_PROPOSALS_HARD_LIMIT,
                        order="by_end_date",
                        order_direction=self.order_direction,
                        status=self.status,
                    )
                    return HarvestedDataRaw(gdpo, searched_proposals, proposal_votes)
                searched_proposals = await node.api.database_api.list_proposals(
                    start=["z"] if self.order_direction == "descending" else ["a"],
                    limit=self.MAX_SEARCHED_PROPOSALS_HARD_LIMIT,
                    order="by_creator",
                    order_direction=self.order_direction,
                    status=self.status,
                )
                return HarvestedDataRaw(gdpo, searched_proposals, proposal_votes)

    async def _sanitize_data(self, data: HarvestedDataRaw) -> SanitizedData:
        return SanitizedData(
            gdpo=self.__assert_gdpo(data.gdpo),
            list_proposals=self.__assert_proposals_list(data.list_proposals),
            list_voted_proposals=self.__assert_proposals_votes(data.list_voted_proposals),
        )

    async def _process_data(self, data: SanitizedData) -> ProposalsData:
        if self.mode == "my_votes_first":
            return ProposalsData(self.__get_top_proposals_with_voted_first(data))
        return ProposalsData(
            proposals=self.__get_prepared_proposals(data.list_proposals, data),
            voted_proposals_ids=self.__get_proposals_ids(data.list_voted_proposals),
        )

    def __create_proposal_data(self, proposal: ProposalSchema, data: SanitizedData) -> Proposal:
        return Proposal(
            title=proposal.subject,
            proposal_id=proposal.proposal_id,
            creator=proposal.creator,
            receiver=proposal.receiver,
            daily_pay=Asset.pretty_amount(proposal.daily_pay),
            votes=humanize_hive_power(
                self.calculate_hp_from_votes(
                    proposal.total_votes, data.gdpo.total_vesting_fund_hive, data.gdpo.total_vesting_shares
                )
            ),
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

    def __get_prepared_proposals(self, proposals: list[ProposalSchema], data: SanitizedData) -> list[Proposal]:
        return [self.__create_proposal_data(proposal, data) for proposal in proposals]

    def __get_proposals_ids(self, proposals: list[ProposalSchema]) -> list[int]:
        proposal_ids: list[int] = []
        for proposal in proposals:
            proposal_ids.append(proposal.proposal_id)

        return proposal_ids

    def __assert_gdpo(self, data: DynamicGlobalProperties | None) -> DynamicGlobalProperties:
        assert data is not None, "DynamicGlobalProperties data is missing"
        return data

    def __assert_proposals_list(self, data: ProposalsList | None) -> list[ProposalSchema]:
        assert data is not None, "ListProposals data is missing"
        return data.proposals

    def __assert_proposals_votes(self, data: ProposalVotes | None) -> list[ProposalSchema]:
        assert data is not None, "ListProposalsVotes data is missing"
        return [
            proposal_vote.proposal for proposal_vote in data.proposal_votes if proposal_vote.voter == self.account_name
        ]

    def __get_today_datetime(self) -> datetime.datetime:
        return datetime.datetime.today().replace(tzinfo=None)

    def calculate_hp_from_votes(
        self, votes: int, total_vesting_fund_hive: Asset.Hive, total_vesting_shares: Asset.Vests
    ) -> int:
        total_vesting_fund = int(total_vesting_fund_hive.amount) / 10**total_vesting_fund_hive.precision
        total_shares = int(total_vesting_shares.amount) / 10**total_vesting_shares.precision

        return (total_vesting_fund * (votes / total_shares)) // 1000000  # type: ignore[no-any-return]