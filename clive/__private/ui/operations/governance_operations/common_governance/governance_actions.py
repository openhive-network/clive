from __future__ import annotations

import contextlib
from abc import abstractmethod
from typing import TYPE_CHECKING, ClassVar

from textual.containers import Horizontal, VerticalScroll
from textual.css.query import NoMatches
from textual.widgets import Label, Static

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.widgets.can_focus_with_scrollbars_only import CanFocusWithScrollbarsOnly

if TYPE_CHECKING:
    from textual.app import ComposeResult


class GovernanceActionRow(Horizontal, AbstractClassMessagePump):
    """Class that displays either the name of the witness or the ID of the proposal - chosen generically based on the action to be performed."""

    def __init__(self, identifier: str, vote: bool, pending: bool = False):
        """
        Initialize the GovernanceActionRow.

        Args:
        ----
        identifier: Used to pass the identifier of the action. It is used to create id of the widget.
        vote: Action to be performed - vote or not.
        pending: Indicates if the operation with such identifier is already in the cart.
        """
        super().__init__(id=self.create_action_row_id(identifier))
        self.__identifier = identifier
        self.__vote = vote
        self.__pending = pending

    def compose(self) -> ComposeResult:
        if self.__pending:
            yield Label("Pending", classes="action-pending action-label")
            yield Label(str(self.action_identifier), classes="action-identifier")
            return

        if self.__vote:
            yield Label("Vote", classes="action-vote action-label")
        else:
            yield Label("Unvote", classes="action-unvote action-label")
        yield Label(str(self.action_identifier), classes="action-identifier")

    @property
    def action_identifier(self) -> str:
        return self.__identifier

    @staticmethod
    @abstractmethod
    def create_action_row_id(identifier: str) -> str:
        pass


class GovernanceActions(VerticalScroll, CanFocusWithScrollbarsOnly):
    """Contains a table of actions to be performed after confirmation."""

    NAME_OF_ACTION: ClassVar[str] = "Action"

    def __init__(self) -> None:
        super().__init__()
        self.__actions_to_perform: dict[str, bool] = {}
        """A dict with action identifier as key and action to pe performed as value"""
        self.__actions_votes = 0

    def compose(self) -> ComposeResult:
        yield Static("Actions to be performed:", id="actions-header")
        with Horizontal(id="name-and-action"):
            yield Static("Action", id="action-row")
            yield Static(self.NAME_OF_ACTION, id="action-name-row")

    async def on_mount(self) -> None:  # type: ignore[override]
        await self.mount_operations_from_cart()

    async def add_row(self, identifier: str, vote: bool = False, pending: bool = False) -> None:
        # check if action is already in the list, if so - return

        with contextlib.suppress(NoMatches):
            self.get_widget_by_id(self.create_action_row_id(identifier))
            return

        await self.mount(self.create_action_row(identifier, vote, pending))

        if vote:
            self.__actions_votes += 1
        else:
            self.__actions_votes -= 1

        if not pending:
            self.add_to_actions(identifier, vote)

        self.hook_on_row_added()

    async def remove_row(self, identifier: str, vote: bool = False) -> None:
        try:
            await self.get_widget_by_id(self.create_action_row_id(identifier)).remove()
        except NoMatches:
            return

        if vote:
            self.__actions_votes -= 1
        else:
            self.__actions_votes += 1

        self.delete_from_actions(identifier)

    def add_to_actions(self, identifier: str, vote: bool) -> None:
        self.__actions_to_perform[identifier] = vote

    def delete_from_actions(self, identifier: str) -> None:
        self.__actions_to_perform.pop(identifier)

    @property
    def actions_votes(self) -> int:
        return self.__actions_votes

    @property
    def actions_to_perform(self) -> dict[str, bool]:
        return self.__actions_to_perform

    def hook_on_row_added(self) -> None:
        """Method to create any action when an action row is added to the action table."""

    @staticmethod
    @abstractmethod
    def create_action_row_id(identifier: str) -> str:
        """Should return id of the action row."""

    @abstractmethod
    async def mount_operations_from_cart(self) -> None:
        """Should check cart and mount all appropriate operations."""

    @abstractmethod
    def create_action_row(self, identifier: str, vote: bool, pending: bool) -> GovernanceActionRow:
        pass
