from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual import on
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Collapsible, SelectionList
from textual.widgets._selection_list import Selection

from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.widgets.buttons import (
    ClearButton,
    SearchButton,
)
from clive.__private.ui.widgets.inputs.authority_filter_input import AuthorityFilterInput
from clive.__private.ui.widgets.inputs.clive_input import CliveInput

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.accounts.accounts import TrackedAccount


class AccountSelectionList(SelectionList[str], CliveWidget):
    """
    Selection list with account names for filtering authorities.

    Attributes:
        ALL_OPTION: Constant for the "all" option in the selection list.

    Args:
        account: The account that will be initially selected.
    """

    ALL_OPTION: Final[str] = "all"

    def __init__(self, account: TrackedAccount) -> None:
        self._initial_checked_account_name = account.name
        super().__init__(*self._create_selections())

    @property
    def is_all_selected(self) -> bool:
        return self.ALL_OPTION in self.selected

    def restore_default(self) -> None:
        self.deselect_all()
        self.select(self.get_option(self._initial_checked_account_name))

    @on(SelectionList.SelectionToggled)
    def _handle_selection(self, event: AccountSelectionList.SelectionToggled[str]) -> None:
        """
        Handle selection toggling -  manage the "all" option behavior and its interaction with other options.

        When "all" is selected, all other options are selected.
        When "all" is deselected, all other options are deselected.
        When any other option is selected while "all" is selected, "all" gets deselected.

        Args:
            event: The event containing the selection list and the toggled selection.
        """
        if event.selection.value == self.ALL_OPTION:
            if self.is_all_selected:
                self.select_all()
            else:
                self.deselect_all()
        elif self.is_all_selected:
            self.deselect(self.ALL_OPTION)

    def _create_selections(self) -> list[Selection[str]]:
        return [Selection(self.ALL_OPTION, self.ALL_OPTION, id="all")] + [
            Selection(
                self._get_selection_prompt(tracked_account.name),
                tracked_account.name,
                initial_state=tracked_account.name is self._initial_checked_account_name,
                id=tracked_account.name,
            )
            for tracked_account in self.profile.accounts.tracked
        ]

    def _get_selection_prompt(self, account_name: str) -> str:
        working_account_name = self.profile.accounts.working.name if self.profile.accounts.working_or_none else None
        return f"{account_name}{' (working)' if working_account_name and account_name is working_account_name else ''}"


class AccountFilterCollapsible(Collapsible):
    BORDER_TITLE = " Authority for accounts "
    TITLE_NO_SELECTION: Final = "no selected accounts"
    TITLE_MULTIPLE_SELECTION: Final = "multiple"

    def __init__(self, account: TrackedAccount) -> None:
        super().__init__(title=account.name)
        self.compose_add_child(AccountSelectionList(account))
        self._initial_title = account.name

    def restore_title(self) -> None:
        self.title = self._initial_title

    @on(AccountSelectionList.SelectionToggled)
    def update_title(self, event: AccountSelectionList.SelectionToggled[str]) -> None:
        selection_list = event.selection_list
        assert isinstance(selection_list, AccountSelectionList), "SelectionList have to be AccountSelectionList."
        selected_accounts = selection_list.selected
        if len(selected_accounts) == 1 or (len(selected_accounts) == 2 and selection_list.is_all_selected):  # noqa: PLR2004
            self.title = next(iter(selected_accounts))
        elif len(selected_accounts) == 0:
            self.title = self.TITLE_NO_SELECTION
        else:
            self.title = self.TITLE_MULTIPLE_SELECTION


class FilterAuthority(Horizontal, CliveWidget):
    DEFAULT_CSS = get_css_from_relative_path(__file__)
    BORDER_TITLE = "Filter authority"

    class AuthorityFilterReady(Message):
        """Message sent when authority filter is ready to be applied."""

    class Cleared(Message):
        """Message sent when authority filter was restored to default."""

    class SelectedAccountsChanged(Message):
        """Message sent when selected accounts in AccountSelectionList were changed."""

    def __init__(self, account: TrackedAccount) -> None:
        super().__init__()
        self._account = account

    def compose(self) -> ComposeResult:
        yield AuthorityFilterInput()
        yield AccountFilterCollapsible(account=self._account)
        yield SearchButton()
        yield ClearButton()

    @property
    def account_filter_collapsible(self) -> AccountFilterCollapsible:
        return self.query_exactly_one(AccountFilterCollapsible)

    @property
    def account_selection_list(self) -> AccountSelectionList:
        return self.query_exactly_one(AccountSelectionList)

    @property
    def selected_options(self) -> list[str]:
        return self.account_selection_list.selected

    @property
    def authority_filter_input(self) -> AuthorityFilterInput:
        return self.query_exactly_one(AuthorityFilterInput)

    @on(AccountSelectionList.SelectionToggled)
    def account_toggled(self, event: AccountSelectionList.SelectionToggled[str]) -> None:
        assert isinstance(event.selection_list, AccountSelectionList), "SelectionList have to be AccountSelectionList."
        self.post_message(self.SelectedAccountsChanged())

    @on(SearchButton.Pressed)
    def request_authority_filter_by_button(self) -> None:
        self._request_authority_filter()

    @on(CliveInput.Submitted)
    def request_authority_filter_by_event(self) -> None:
        self._request_authority_filter()

    @on(ClearButton.Pressed)
    async def clear_filters(self) -> None:
        self.apply_default_filter()
        self.post_message(self.Cleared())

    def apply_default_filter(self) -> None:
        self.authority_filter_input.clear_validation()
        self.account_selection_list.restore_default()
        self.account_filter_collapsible.restore_title()
        self.collapse_account_filter_collapsible()

    def collapse_account_filter_collapsible(self) -> None:
        self.account_filter_collapsible.collapsed = True

    def _request_authority_filter(self) -> None:
        self.post_message(self.AuthorityFilterReady())
