from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from textual import on
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import Label

from clive.__private.core.commands.data_retrieval.proposals_data import Proposal as ProposalData
from clive.__private.core.commands.data_retrieval.proposals_data import ProposalsDataRetrieval
from clive.__private.core.constants.node import MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION
from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.models.schemas import UpdateProposalVotesOperation
from clive.__private.ui.data_providers.proposals_data_provider import ProposalsDataProvider
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.screens.operations.governance_operations.common_governance.governance_actions import (
    GovernanceActionRow,
    GovernanceActions,
)
from clive.__private.ui.screens.operations.governance_operations.common_governance.governance_tab_pane import (
    GovernanceTabPane,
)
from clive.__private.ui.screens.operations.governance_operations.common_governance.governance_table import (
    GovernanceListHeader,
    GovernanceListWidget,
    GovernanceTable,
    GovernanceTableRow,
)
from clive.__private.ui.widgets.clive_basic.clive_select import CliveSelect
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section_title import SectionTitle

if TYPE_CHECKING:
    from typing import Final

    from textual.app import ComposeResult
    from typing_extensions import TypeIs


class ProposalsOrderSelect(CliveSelect[ProposalsDataRetrieval.Orders]):
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


class ProposalsOrderDirectionSelect(CliveSelect[ProposalsDataRetrieval.OrderDirections]):
    SELECTABLES: Final[list[tuple[str, ProposalsDataRetrieval.OrderDirections]]] = [
        (value.capitalize(), value) for value in ProposalsDataRetrieval.ORDER_DIRECTIONS
    ]

    def __init__(self) -> None:
        super().__init__(
            options=self.SELECTABLES,
            value=ProposalsDataRetrieval.DEFAULT_ORDER_DIRECTION,
            allow_blank=False,
        )


class ProposalsStatusSelect(CliveSelect[ProposalsDataRetrieval.Statuses]):
    SELECTABLES: Final[list[tuple[str, ProposalsDataRetrieval.Statuses]]] = [
        (value.capitalize(), value) for value in ProposalsDataRetrieval.STATUSES
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
    """Check if there is a proposal in the action table - if so, move True to the GovernanceCheckbox parameter."""

    def create_row_content(self) -> ComposeResult:
        yield ProposalInformation(self.row_data, self.evenness)

    @property
    def action_identifier(self) -> str:
        return str(self.row_data.proposal_id)

    def get_action_row_id(self) -> str:
        return ProposalActionRow.create_action_row_id(self.action_identifier)

    @property
    def is_operation_in_cart(self) -> bool:
        for operation in self.profile.transaction:
            if (
                isinstance(operation, UpdateProposalVotesOperation)
                and self.row_data.proposal_id in operation.proposal_ids
            ):
                return True
        return False


class ProposalActionRow(GovernanceActionRow):
    @staticmethod
    def create_action_row_id(identifier: str) -> str:
        return f"proposal{identifier}-action-row"


class ProposalsActions(GovernanceActions[UpdateProposalVotesOperation]):
    NAME_OF_ACTION: ClassVar[str] = "Proposal"

    async def mount_operations_from_cart(self) -> None:
        for operation in self.profile.transaction:
            if self.should_be_added_to_actions(operation):
                for proposal_id in operation.proposal_ids:
                    await self.add_row(identifier=str(proposal_id), vote=operation.approve)

    def should_be_added_to_actions(self, operation: object) -> TypeIs[UpdateProposalVotesOperation]:
        return (
            isinstance(operation, UpdateProposalVotesOperation)
            and operation.voter == self.profile.accounts.working.name
        )

    def create_action_row(self, identifier: str, *, vote: bool) -> GovernanceActionRow:
        return ProposalActionRow(identifier, vote=vote)

    @staticmethod
    def create_action_row_id(identifier: str) -> str:
        return ProposalActionRow.create_action_row_id(identifier)

    def add_operation_to_cart(self, identifier: str, *, vote: bool = False) -> None:
        proposal_id = int(identifier)

        for op in self.profile.transaction:
            if not isinstance(op, UpdateProposalVotesOperation):
                continue

            if proposal_id in op.proposal_ids:
                return

            if op.approve == vote and len(op.proposal_ids) < MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION:
                op.proposal_ids.append(proposal_id)  # type: ignore[arg-type]
                op.proposal_ids.sort()  # proposal id's must be sorted
                return

        self.profile.transaction.add_operation(
            UpdateProposalVotesOperation(
                voter=self.profile.accounts.working.name,
                proposal_ids=[proposal_id],
                approve=vote,
            )
        )

    def remove_operation_from_cart(self, identifier: str, *, vote: bool = False) -> None:
        proposal_id = int(identifier)

        for op in self.profile.transaction:
            if not isinstance(op, UpdateProposalVotesOperation):
                continue

            if op.approve == vote and proposal_id in op.proposal_ids:
                if len(op.proposal_ids) == 1:
                    self.profile.transaction.remove_operation(op)
                    return

                op.proposal_ids.remove(proposal_id)  # type: ignore[arg-type]

    @property
    def provider(self) -> ProposalsDataProvider:
        return self.screen.query_exactly_one(ProposalsDataProvider)


class ProposalsList(GovernanceListWidget[ProposalData]):
    def _create_row(self, data: ProposalData, *, even: bool = False) -> Proposal:
        return Proposal(data, even=even)


class ProposalsListHeader(GovernanceListHeader):
    def create_custom_columns(self) -> ComposeResult:
        yield SectionTitle(
            f"Votes for proposals cast by your proxy ({self.profile.accounts.working.data.proxy})"
            if self.is_proxy_set
            else "Update your proposal votes"
        )


class ProposalsTable(GovernanceTable[ProposalData, ProposalsDataProvider]):
    async def change_order(
        self,
        order: ProposalsDataRetrieval.Orders,
        order_direction: ProposalsDataRetrieval.OrderDirections,
        status: ProposalsDataRetrieval.Statuses,
    ) -> None:
        await self.provider.change_order(order=order, order_direction=order_direction, status=status).wait()
        await self.reset_page()

    def create_header(self) -> GovernanceListHeader:
        return ProposalsListHeader()

    def create_new_list_widget(self) -> GovernanceListWidget[ProposalData]:
        return ProposalsList(self.data_chunk)

    @property
    def provider(self) -> ProposalsDataProvider:
        return self.screen.query_exactly_one(ProposalsDataProvider)

    @property
    def data(self) -> list[ProposalData]:
        return self.provider.content.proposals


class ProposalsOrderChange(Vertical):
    @dataclass
    class Search(Message):
        """Emitted when any selector changed."""

        order_by: ProposalsDataRetrieval.Orders
        order_direction: ProposalsDataRetrieval.OrderDirections
        status: ProposalsDataRetrieval.Statuses

    def __init__(self) -> None:
        super().__init__()

        with self.prevent(CliveSelect.Changed):
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

    @on(CliveSelect.Changed)
    def search_witnesses(self) -> None:
        order_by = self.__order_by_select.selection_ensure
        order_direction = self.__order_direction_select.selection_ensure
        status = self.__proposal_status_select.selection_ensure
        self.post_message(self.Search(order_by, order_direction, status))


class Proposals(GovernanceTabPane):
    """TabPane with all content about proposals."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self) -> None:
        super().__init__(title="Proposals", id="proposals")

    def compose(self) -> ComposeResult:
        self.__proposals_table = ProposalsTable()
        yield ProposalsOrderChange()
        with ScrollablePart(), Horizontal(classes="vote-actions"):
            yield self.__proposals_table
            yield ProposalsActions()

    @on(ProposalsOrderChange.Search)
    async def change_order(self, message: ProposalsOrderChange.Search) -> None:
        await self.__proposals_table.change_order(
            order=message.order_by, order_direction=message.order_direction, status=message.status
        )
