from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.events import Click
from textual.message import Message
from textual.widgets import Label, Select, Static, TabPane
from textual.widgets._select import NoSelection

from clive.__private.core.commands.data_retrieval.proposals_data import ProposalsDataRetrieval
from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.ui.data_providers.proposals_data_provider import ProposalsDataProvider
from clive.__private.ui.operations.bindings.operation_action_bindings import OperationActionBindings
from clive.__private.ui.operations.governance_operations.governance_checkbox import GovernanceCheckbox
from clive.__private.ui.widgets.can_focus_with_scrollbars_only import CanFocusWithScrollbarsOnly
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from schemas.operations.update_proposal_votes_operation import UpdateProposalVotesOperation

if TYPE_CHECKING:
    from typing import Final

    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.__private.core.commands.data_retrieval.proposals_data import Proposal as ProposalData
    from clive.models import Operation

MAX_PROPOSALS_ON_PAGE: Final[int] = 10


class ScrollablePart(ScrollableContainer, can_focus=False):
    pass


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
            yield Label(
                f"by {self.__proposal.creator} for {self.__proposal.receiver}",
                classes=f"proposal-row-{self.__evenness} proposal-accounts",
            )
            if self.__proposal.status == "active":
                yield Label(
                    f"Ends: {humanize_datetime(self.__proposal.end_date)[:10]}",
                    classes=f"proposal-row-{self.__evenness} proposal-date",
                )


class Proposal(Horizontal, CliveWidget, can_focus=True):
    """The class first checks if there is a proposal in the action table - if so, move True to the GovernanceCheckbox parameter."""

    BINDINGS = [
        Binding("pageup", "previous_page", "PgDn"),
        Binding("pagedown", "next_page", "PgUp"),
        Binding("enter", "toggle_checkbox", "", show=False),
    ]

    def __init__(self, proposal: ProposalData, evenness: str = "even") -> None:
        super().__init__()
        self.__proposal = proposal
        self.__evenness = evenness

        self.governance_checkbox = GovernanceCheckbox(
            is_voted=proposal.voted,
            initial_state=self.is_already_in_proposal_actions_container or self.is_proposal_operation_in_cart,
            disabled=bool(self.app.world.profile_data.working_account.data.proxy) or self.is_proposal_operation_in_cart,
        )

    def on_mount(self) -> None:
        self.watch(self.governance_checkbox, "disabled", callback=self.dimm_on_disabled_checkbox)

    def compose(self) -> ComposeResult:
        yield self.governance_checkbox
        yield ProposalInformation(self.__proposal, self.__evenness)

    async def move_proposal_to_actions(self) -> None:
        proposal_actions = self.app.query_one(ProposalsActions)
        if self.governance_checkbox.value:
            await proposal_actions.mount_proposal(
                self.__proposal.proposal_id, voted=self.__proposal.voted, pending=self.is_proposal_operation_in_cart
            )
            return
        await proposal_actions.unmount_proposal(self.__proposal.proposal_id)

    def dimm_on_disabled_checkbox(self, value: bool) -> None:
        if value:
            self.add_class("dimmed")
            return
        self.remove_class("dimmed")

    @on(GovernanceCheckbox.Clicked)
    def focus_myself(self) -> None:
        self.focus()

    @on(GovernanceCheckbox.Changed)
    async def modify_action_status(self) -> None:
        await self.move_proposal_to_actions()

    async def action_next_page(self) -> None:
        await self.app.query_one(ProposalsTable).next_page()

    async def action_previous_page(self) -> None:
        await self.app.query_one(ProposalsTable).previous_page()

    def action_toggle_checkbox(self) -> None:
        self.governance_checkbox.toggle()

    @property
    def is_proposal_operation_in_cart(self) -> bool:
        for operation in self.app.world.profile_data.cart:
            if (
                isinstance(operation, UpdateProposalVotesOperation)
                and self.__proposal.proposal_id in operation.proposal_ids
            ):
                return True
        return False

    @property
    def is_already_in_proposal_actions_container(self) -> bool:
        try:
            self.app.query_one(ProposalsActions.get_proposal_action_row(self.__proposal.proposal_id))
        except NoMatches:
            return False
        else:
            return True


class ProposalActionRow(Horizontal):
    def __init__(self, proposal_id: int, voted: bool = False, pending: bool = False):
        super().__init__(id=f"proposal{proposal_id}-action-row")
        self.__proposal_id = proposal_id
        self.__pending = pending
        self.__voted = voted

    def compose(self) -> ComposeResult:
        if self.__pending:
            yield Label("Pending", classes="action-pending action-label")
            yield Label(f"#{self.__proposal_id}", classes="action-proposal-id")
            return

        if not self.__voted:
            yield Label("Vote", classes="action-vote action-label")
        else:
            yield Label("Unvote", classes="action-unvote action-label")
        yield Label(f"#{self.__proposal_id}", classes="action-proposal-id")


class ProposalsActions(VerticalScroll, CanFocusWithScrollbarsOnly):
    """
    Contains a table of operations to be performed after confirmation.

    Attributes
    ----------
    __actions_to_perform (dict): a dict with proposal_id as key and action to pe performed as key
    """

    def __init__(self) -> None:
        super().__init__()
        self.__actions_to_perform: dict[int, bool] = {}

    def compose(self) -> ComposeResult:
        yield Static("Actions to be performed:", id="witnesses-actions-header")
        with Horizontal(id="name-and-action"):
            yield Static("Action", id="action-proposal-row")
            yield Static("Proposal", id="proposal-id-actions-row")

    async def on_mount(self) -> None:  # type: ignore[override]
        for operation in self.app.world.profile_data.cart:
            if isinstance(operation, UpdateProposalVotesOperation):
                for proposal in operation.proposal_ids:
                    await self.mount_proposal(proposal_id=proposal, pending=True)

    async def mount_proposal(self, proposal_id: int, voted: bool = False, pending: bool = False) -> None:
        # check if proposal is already in the list, if so - return
        with contextlib.suppress(NoMatches):
            self.query_one(self.get_proposal_action_row(proposal_id))
            return

        await self.mount(ProposalActionRow(proposal_id, voted=voted, pending=pending))

        if not pending:
            self.__actions_to_perform[proposal_id] = not voted

    async def unmount_proposal(self, proposal_id: int) -> None:
        try:
            await self.query_one(self.get_proposal_action_row(proposal_id)).remove()
        except NoMatches:
            return

        self.__actions_to_perform.pop(proposal_id)

    @staticmethod
    def get_proposal_action_row(proposal_id: int) -> str:
        return f"#proposal{proposal_id}-action-row"

    @property
    def actions_to_perform(self) -> dict[int, bool]:
        return self.__actions_to_perform

    @property
    def provider(self) -> ProposalsDataProvider:
        return self.app.query_one(ProposalsDataProvider)


class ProposalsList(Vertical, CliveWidget):
    def __init__(
        self,
        proposals: list[ProposalData] | None,
    ) -> None:
        super().__init__()
        self.__proposals_to_display = proposals if proposals is not None else None

    def compose(self) -> ComposeResult:
        if self.__proposals_to_display is None:
            self.loading = True
            return

        if len(self.__proposals_to_display) == 0:
            yield Static("No proposals according to specific filters!")
            return

        for id_, proposal in enumerate(self.__proposals_to_display):
            if id_ % 2 == 0:
                yield Proposal(proposal)
            else:
                yield Proposal(proposal, evenness="odd")


class ArrowUpWidget(Static):
    def __init__(self) -> None:
        super().__init__(renderable="↑ PgUp")

    @on(Click)
    async def previous_page(self) -> None:
        await self.app.query_one(ProposalsTable).previous_page()


class ArrowDownWidget(Static):
    def __init__(self) -> None:
        super().__init__(renderable="↓ PgDn")

    @on(Click)
    async def next_page(self) -> None:
        await self.app.query_one(ProposalsTable).next_page()


class ProposalsListHeader(Horizontal):
    def __init__(self) -> None:
        super().__init__()
        self.arrow_up = ArrowUpWidget()
        self.arrow_down = ArrowDownWidget()

        self.arrow_up.visible = False

    def compose(self) -> ComposeResult:
        yield self.arrow_up
        yield Static("Update your proposal votes", id="proposals-header-column")
        yield self.arrow_down


class ProposalsTable(Vertical, CliveWidget, can_focus=False):
    def __init__(self) -> None:
        super().__init__()

        self.__proposal_index = 0
        self.__header = ProposalsListHeader()
        self.__is_loading = True

    def compose(self) -> ComposeResult:
        yield self.__header
        yield ProposalsList(self.proposals_chunk)

    async def __set_loading(self) -> None:
        self.__is_loading = True
        with contextlib.suppress(NoMatches):
            witness_list = self.query_one(ProposalsList)
            await witness_list.query("*").remove()
            await witness_list.mount(Label("Loading..."))

    def __set_loaded(self) -> None:
        self.__is_loading = False

    async def reset_page(self) -> None:
        """During reset we cannot call __sync_witness_list because we have to wait for the provider to update the data."""
        self.__proposal_index = 0
        self.__header.arrow_up.visible = False
        self.__header.arrow_down.visible = True

        if not self.__is_loading:
            await self.__sync_proposals_list()

    async def next_page(self) -> None:
        if self.__is_loading:
            return

        # It is used to prevent the user from switching to an empty page by key binding
        if self.amount_of_fetched_proposals - MAX_PROPOSALS_ON_PAGE <= self.__proposal_index + 1:
            self.notify("No proposals on the next page", severity="warning")
            return

        self.__proposal_index += MAX_PROPOSALS_ON_PAGE

        self.__header.arrow_up.visible = True

        if self.amount_of_fetched_proposals - MAX_PROPOSALS_ON_PAGE <= self.__proposal_index:
            self.__header.arrow_down.visible = False

        await self.__sync_proposals_list(focus_first_proposal=True)

    async def previous_page(self) -> None:
        if self.__is_loading:
            return

        # It is used to prevent the user going to a page with a negative index by key binding
        if self.__proposal_index <= 0:
            self.notify("No proposals on the previous page", severity="warning")
            return

        self.__header.arrow_down.visible = True

        self.__proposal_index -= MAX_PROPOSALS_ON_PAGE

        if self.__proposal_index <= 0:
            self.__header.arrow_up.visible = False

        await self.__sync_proposals_list(focus_first_proposal=True)

    def on_mount(self) -> None:
        self.watch(self.provider, "content", callback=lambda: self.__sync_proposals_list())

    async def change_order(self, mode: str, order_direction: str, status: str) -> None:
        await self.provider.change_order(mode=mode, order_direction=order_direction, status=status).wait()
        await self.reset_page()

    async def __sync_proposals_list(self, focus_first_proposal: bool = False) -> None:
        await self.__set_loading()

        new_proposals_list = ProposalsList(self.proposals_chunk)

        with self.app.batch_update():
            await self.query(ProposalsList).remove()
            await self.mount(new_proposals_list)

        if focus_first_proposal:
            first_proposal = self.query(Proposal).first()
            first_proposal.focus()

        self.__set_loaded()

    @property
    def amount_of_fetched_proposals(self) -> int:
        return len(self.provider.content.proposals)

    @property
    def proposals_chunk(self) -> list[ProposalData] | None:
        if self.provider.content.proposals is None:
            return None
        return self.provider.content.proposals[self.__proposal_index : self.__proposal_index + MAX_PROPOSALS_ON_PAGE]

    @property
    def provider(self) -> ProposalsDataProvider:
        return self.app.query_one(ProposalsDataProvider)


class ProposalsOrderChange(Vertical):
    AVAILABLE_MODES: Final[list[str]] = [
        "total_votes",
        "my_votes_first",
        "start_date",
        "end_date",
        "creator",
    ]
    AVAILABLE_STATUS: Final[list[str]] = ["active", "votable", "inactive", "all", "expired", "inactive"]
    ORDER_DIRECTIONS: Final[list[str]] = ["descending", "ascending"]

    @dataclass
    class Search(Message):
        """Emitted when any selector changed."""

        order_by: ProposalsDataRetrieval.Modes
        order_direction: ProposalsDataRetrieval.OrderDirections
        status: ProposalsDataRetrieval.ProposalStatus

    def __init__(self) -> None:
        super().__init__()
        self.__order_by_choose = Select(
            ((mode, mode) for mode in self.AVAILABLE_MODES),
            prompt="Order by",
        )
        self.__order_direction_choose = Select(
            ((order_direction, order_direction) for order_direction in self.ORDER_DIRECTIONS),
            prompt="Order direction",
        )
        self.__proposal_status_choose = Select(
            ((status, status) for status in self.AVAILABLE_STATUS),
            prompt="Status",
        )

    def compose(self) -> ComposeResult:
        with Horizontal(id="selectors-labels"):
            yield Label("Search by")
            yield Label("Order direction")
            yield Label("Status")
        with Horizontal(id="order-list-selectors"):
            yield self.__order_by_choose
            yield self.__order_direction_choose
            yield self.__proposal_status_choose

    @on(Select.Changed)
    def search_witnesses(self) -> None:
        order_by = (
            "search_by" + str(self.__order_by_choose.value)
            if not isinstance(self.__order_by_choose.value, NoSelection)
            else ProposalsDataRetrieval.DEFAULT_MODE
        )
        order_direction = (
            str(self.__order_direction_choose.value)
            if not isinstance(self.__order_direction_choose.value, NoSelection)
            else ProposalsDataRetrieval.DEFAULT_ORDER_DIRECTION
        )
        status = (
            str(self.__proposal_status_choose.value)
            if not isinstance(self.__proposal_status_choose.value, NoSelection)
            else ProposalsDataRetrieval.DEFAULT_STATUS
        )

        self.post_message(self.Search(order_by, order_direction, status))


class Proposals(TabPane, OperationActionBindings):
    """TabPane with all content about proposals."""

    def __init__(self, title: TextType) -> None:
        super().__init__(title=title)

    def compose(self) -> ComposeResult:
        self.__proposals_table = ProposalsTable()

        with ScrollablePart(), Horizontal(id="proposals-vote-actions"):
            yield self.__proposals_table
            yield ProposalsActions()
        yield ProposalsOrderChange()

    @on(ProposalsOrderChange.Search)
    async def change_order(self, message: ProposalsOrderChange.Search) -> None:
        await self.__proposals_table.change_order(
            mode=message.order_by, order_direction=message.order_direction, status=message.status
        )

    def _create_operations(self) -> list[Operation] | None:
        working_account_name = self.app.world.profile_data.working_account.name
        operations_to_perform = self.app.query_one(ProposalsActions).actions_to_perform

        operations_to_return: list[Operation] = []

        proposals_to_vote = [proposal_id for proposal_id, approve in operations_to_perform.items() if approve]
        proposals_to_unvote = [proposal_id for proposal_id, approve in operations_to_perform.items() if not approve]

        if not proposals_to_vote and not proposals_to_unvote:
            return None

        if proposals_to_vote:
            proposals_to_vote.sort()
            vote_operation = UpdateProposalVotesOperation(
                voter=working_account_name,
                proposal_ids=proposals_to_vote,
                approve=True,
                extensions=[],
            )
            operations_to_return.append(vote_operation)

        if proposals_to_unvote:
            proposals_to_unvote.sort()
            unvote_operation = UpdateProposalVotesOperation(
                voter=working_account_name,
                proposal_ids=proposals_to_unvote,
                approve=False,
                extensions=[],
            )
            operations_to_return.append(unvote_operation)

        return operations_to_return
