from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from textual import on
from textual.containers import Horizontal, Vertical
from textual.css.query import NoMatches
from textual.message import Message
from textual.widgets import Label, Select, Static, TabPane

from clive.__private.core.commands.data_retrieval.proposals_data import Proposal as ProposalData
from clive.__private.core.commands.data_retrieval.proposals_data import ProposalsDataRetrieval
from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.ui.data_providers.proposals_data_provider import ProposalsDataProvider
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.operations.bindings.operation_action_bindings import OperationActionBindings
from clive.__private.ui.operations.governance_operations.common_governance.common_elements import (
    GovernanceActionRow,
    GovernanceActions,
    GovernanceListHeader,
    GovernanceListWidget,
    GovernanceTable,
    GovernanceTableRow,
    ScrollablePart,
)
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from schemas.operations.update_proposal_votes_operation import UpdateProposalVotesOperation

if TYPE_CHECKING:
    from typing import Final

    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.models import Operation

MAX_PROPOSALS_ON_PAGE: Final[int] = 10
MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION: Final[int] = 5


class ProposalsOrderSelect(Select[ProposalsDataRetrieval.Orders]):
    SELECTABLES: Final[list[tuple[str, ProposalsDataRetrieval.Orders]]] = [
        ("Total votes, mine first", "by_total_votes_with_voted_first"),
        ("Total votes", "by_total_votes"),
        ("Start date", "by_start_date"),
        ("End date", "by_end_date"),
        ("Creator", "by_creator"),
    ]

    def __init__(self) -> None:
        super().__init__(
            options=self.SELECTABLES,
            value=ProposalsDataRetrieval.DEFAULT_ORDER,
            allow_blank=False,
        )


class ProposalsOrderDirectionSelect(Select[ProposalsDataRetrieval.OrderDirections]):
    SELECTABLES: Final[list[tuple[str, ProposalsDataRetrieval.OrderDirections]]] = [
        (value.capitalize(), value) for value in ProposalsDataRetrieval.OrderDirections.__args__
    ]

    def __init__(self) -> None:
        super().__init__(
            options=self.SELECTABLES,
            value=ProposalsDataRetrieval.DEFAULT_ORDER_DIRECTION,
            allow_blank=False,
        )


class ProposalsStatusSelect(Select[ProposalsDataRetrieval.Statuses]):
    SELECTABLES: Final[list[tuple[str, ProposalsDataRetrieval.Statuses]]] = [
        (value.capitalize(), value) for value in ProposalsDataRetrieval.Statuses.__args__
    ]

    def __init__(self) -> None:
        super().__init__(
            options=self.SELECTABLES,
            value=ProposalsDataRetrieval.DEFAULT_STATUS,
            allow_blank=False,
        )


class ProposalInformation(Vertical):
    def __init__(self, proposal: ProposalData, evenness: str) -> None:
        super().__init__()
        self.__proposal = proposal
        self.__evenness = evenness

    def compose(self) -> ComposeResult:
        with Horizontal(classes="row-proposal-information"):
            yield Label(f"#{self.__proposal.proposal_id}", classes=f"proposal-id-{self.__evenness} proposal-id")
            yield Label(self.__proposal.status, classes=f"proposal-row-{self.__evenness} proposal-status")
            yield Label(self.__proposal.votes, classes=f"proposal-row-{self.__evenness} proposal-votes")
            yield Label(
                f"Daily: {self.__proposal.daily_pay} HBD", classes=f"proposal-row-{self.__evenness} proposal-pay"
            )
        with Horizontal(classes="row-proposal-information"):
            yield EllipsedStatic(self.__proposal.title, classes=f"proposal-row-{self.__evenness} proposal-title")
        with Horizontal(classes="row-proposal-information"):
            yield Label(self.__get_receiver_info(), classes=f"proposal-row-{self.__evenness} proposal-accounts")
            yield Label(
                (
                    f"{humanize_datetime(self.__proposal.start_date, with_time=False)} -"
                    f" {humanize_datetime(self.__proposal.end_date, with_time=False)}"
                ),
                classes=f"proposal-row-{self.__evenness} proposal-date",
            )

    def __get_receiver_info(self) -> str:
        message = f"by {self.__proposal.creator}"
        if self.__proposal.creator != self.__proposal.receiver:
            message += f" for {self.__proposal.receiver}"
        return message


class Proposal(GovernanceTableRow[ProposalData]):
    """The class first checks if there is a proposal in the action table - if so, move True to the GovernanceCheckbox parameter."""

    def create_row_content(self) -> ComposeResult:
        yield ProposalInformation(self.row_data, self.evenness)

    @property
    def actions_type(self) -> type[ProposalsActions]:  # type: ignore[override]
        return ProposalsActions

    @property
    def action_identifier(self) -> int:  # type: ignore[override]
        return self.row_data.proposal_id

    @property
    def is_operation_in_cart(self) -> bool:
        for operation in self.app.world.profile_data.cart:
            if (
                isinstance(operation, UpdateProposalVotesOperation)
                and self.row_data.proposal_id in operation.proposal_ids
            ):
                return True
        return False

    @property
    def is_already_in_actions_container(self) -> bool:
        try:
            self.app.query_one(ProposalsActions.get_action_id(identifier=self.row_data.proposal_id))
        except NoMatches:
            return False
        else:
            return True


class ProposalActionRow(GovernanceActionRow[int]):
    def create_widget_id(self) -> str:
        return f"proposal{self.action_identifier}-action-row"


class ProposalsActions(GovernanceActions[int]):
    async def mount_operations_from_cart(self) -> None:
        for operation in self.app.world.profile_data.cart:
            if isinstance(operation, UpdateProposalVotesOperation):
                for proposal in operation.proposal_ids:
                    await self.mount_action(identifier=proposal, pending=True)

    def create_action_row(self, identifier: int, vote: bool, pending: bool) -> GovernanceActionRow[int]:
        return ProposalActionRow(identifier, vote, pending)

    def create_number_of_votes_restriction(self) -> None:
        """Proposals Tab has not restriction about the number of votes."""

    @staticmethod
    def get_action_id(identifier: int) -> str:
        return f"#proposal{identifier}-action-row"

    @property
    def name_of_action(self) -> str:
        return "Proposal"

    @property
    def provider(self) -> ProposalsDataProvider:
        return self.app.query_one(ProposalsDataProvider)


class ProposalsList(GovernanceListWidget[ProposalData]):
    def show_elements(self) -> ComposeResult:
        if self.elements_to_display is not None:
            for id_, proposal in enumerate(self.elements_to_display):
                if id_ % 2 == 0:
                    yield Proposal(proposal, table_selector=type(self.app.query_one(ProposalsTable)))
                else:
                    yield Proposal(proposal, table_selector=type(self.app.query_one(ProposalsTable)), evenness="odd")


class PlaceTaker(Static):
    pass


class ProposalsListHeader(GovernanceListHeader):
    def create_custom_columns(self) -> ComposeResult:
        yield Static("Update your proposal votes", id="proposals-header-column")

    def create_additional_headlines(self) -> ComposeResult:
        """Proposals header has no additional headline."""
        yield PlaceTaker()


class ProposalsTable(GovernanceTable):
    async def change_order(self, order: str, order_direction: str, status: str) -> None:
        await self.provider.change_order(order=order, order_direction=order_direction, status=status).wait()
        await self.reset_page()

    def create_header(self) -> GovernanceListHeader:
        return ProposalsListHeader(table_selector=type(self))

    @property
    def list_widget_type(self) -> type[GovernanceListWidget[ProposalData]]:  # type: ignore[override]
        return ProposalsList

    @property
    def row_widget_type(self) -> type[GovernanceTableRow[ProposalData]]:  # type: ignore[override]
        return Proposal

    def create_new_list_widget(self) -> GovernanceListWidget[ProposalData]:  # type: ignore[override]
        return ProposalsList(self.proposals_chunk)

    @property
    def max_elements_on_page(self) -> int:
        return MAX_PROPOSALS_ON_PAGE

    @property
    def amount_of_fetched_elements(self) -> int:
        return len(self.provider.content.proposals)

    @property
    def proposals_chunk(self) -> list[ProposalData] | None:
        if not self.provider.updated:
            return None
        return self.provider.content.proposals[self.element_index : self.element_index + MAX_PROPOSALS_ON_PAGE]

    @property
    def provider(self) -> ProposalsDataProvider:  # type: ignore[override]
        return self.app.query_one(ProposalsDataProvider)


class ProposalsOrderChange(Vertical):
    @dataclass
    class Search(Message):
        """Emitted when any selector changed."""

        order_by: ProposalsDataRetrieval.Orders
        order_direction: ProposalsDataRetrieval.OrderDirections
        status: ProposalsDataRetrieval.Statuses

    def __init__(self) -> None:
        super().__init__()
        self.__order_by_select = ProposalsOrderSelect()
        self.__order_direction_select = ProposalsOrderDirectionSelect()
        self.__proposal_status_select = ProposalsStatusSelect()

    def compose(self) -> ComposeResult:
        with Horizontal(id="selectors-labels"):
            yield Label("Order by")
            yield Label("Order direction")
            yield Label("Status")
        with Horizontal(id="order-list-selectors"):
            yield self.__order_by_select
            yield self.__order_direction_select
            yield self.__proposal_status_select

    @on(Select.Changed)
    def search_witnesses(self) -> None:
        order_by = self.__order_by_select.value
        order_direction = self.__order_direction_select.value
        status = self.__proposal_status_select.value
        self.post_message(self.Search(order_by, order_direction, status))


class Proposals(TabPane, OperationActionBindings):
    """TabPane with all content about proposals."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: TextType) -> None:
        super().__init__(title=title)

    def compose(self) -> ComposeResult:
        self.__proposals_table = ProposalsTable()

        with ScrollablePart(), Horizontal(classes="vote-actions"):
            yield self.__proposals_table
            yield ProposalsActions()
        yield ProposalsOrderChange()

    @on(ProposalsOrderChange.Search)
    async def change_order(self, message: ProposalsOrderChange.Search) -> None:
        await self.__proposals_table.change_order(
            order=message.order_by, order_direction=message.order_direction, status=message.status
        )

    def _create_operations(self) -> list[Operation] | None:
        working_account_name = self.app.world.profile_data.working_account.name

        batched_proposals_ids_to_unvote = self.__split_proposals(approve=False)
        batched_proposals_ids_to_vote = self.__split_proposals(approve=True)

        if not batched_proposals_ids_to_unvote and not batched_proposals_ids_to_vote:
            return None

        return self.__create_vote_operations(
            batched_proposals_ids_to_vote, working_account_name, approve=True
        ) + self.__create_vote_operations(
            batched_proposals_ids_to_unvote, working_account_name, approve=False
        )  # type: ignore[return-value]

    def __create_vote_operations(
        self, batched_proposal_ids: list[list[int]], working_account_name: str, approve: bool
    ) -> list[UpdateProposalVotesOperation]:
        return [
            UpdateProposalVotesOperation(
                voter=working_account_name,
                proposal_ids=proposal_ids,
                approve=approve,
                extensions=[],
            )
            for proposal_ids in batched_proposal_ids
        ]

    def __split_proposals(self, approve: bool = True) -> list[list[int]]:
        operations_to_perform = self.app.query_one(ProposalsActions).actions_to_perform
        proposals_ids_to_return = [
            proposal_id for proposal_id, action_approve in operations_to_perform.items() if action_approve == approve
        ]
        proposals_ids_to_return.sort()

        return [
            proposals_ids_to_return[i : i + MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION]
            for i in range(0, len(proposals_ids_to_return), MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION)
        ]