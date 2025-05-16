from __future__ import annotations

from typing import TYPE_CHECKING, Literal

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
from clive.__private.ui.widgets.inputs.authority_input import AuthorityInput
from clive.__private.ui.widgets.inputs.clive_input import CliveInput

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.accounts.accounts import TrackedAccount


class AccountSelectionList(SelectionList[str], CliveWidget):
    """Selection list with account names for filtering authorities."""

    def __init__(self, account: TrackedAccount) -> None:
        self._initial_checked_account_name = account.name
        working_account_name = self.profile.accounts.working.name if self.profile.accounts.working_or_none else None
        self._filter_entries = [Selection("all", "all")] + [
            Selection(
                f"{tracked_account.name}{
                    ' (working)' if working_account_name and tracked_account.name is working_account_name else ''
                }",
                tracked_account.name,
                initial_state=tracked_account.name is self._initial_checked_account_name,
            )
            for tracked_account in self.profile.accounts.tracked
        ]
        super().__init__(*self._filter_entries)

    def restore_default(self) -> None:
        self.deselect_all()
        all_selections = [self.get_option_at_index(index) for index in range(len(self.profile.accounts.tracked) + 1)]
        for selection in all_selections:
            if selection.value == self._initial_checked_account_name:
                self.select(selection)

    @on(SelectionList.SelectionToggled)
    def _handle_options_in_filter(self, event: AccountSelectionList.SelectionToggled[str]) -> None:
        def change_every_option_except_all_option(*, action: Literal["select", "deselect"]) -> None:
            for selection in all_selections:
                if selection.value != "all":
                    selection_list.select(selection) if action == "select" else selection_list.deselect(selection)

        index = event.selection_index
        selection_list = event.selection_list
        option_toggled = selection_list.get_option_at_index(index)
        all_selections = [
            selection_list.get_option_at_index(index) for index in range(len(self.profile.accounts.tracked) + 1)
        ]

        if option_toggled.value == "all":
            if "all" in selection_list.selected:
                change_every_option_except_all_option(action="select")
            else:
                change_every_option_except_all_option(action="deselect")
        else:
            selection_for_all_accounts = selection_list.get_option_at_index(0)
            if "all" in selection_list.selected:
                selection_list.deselect(selection_for_all_accounts)


class AccountFilterCollapsible(Collapsible):
    BORDER_TITLE = " Authority for accounts "

    def __init__(self, initial_title: str) -> None:
        super().__init__(title=initial_title)
        self._initial_title = initial_title

    def restore_title(self) -> None:
        self.title = self._initial_title

    def update_title(self, selected_accounts: list[str]) -> None:
        if len(selected_accounts) == 1 or (len(selected_accounts) == 2 and "all" in selected_accounts):  # noqa: PLR2004
            self.title = next(iter(selected_accounts))
        elif len(selected_accounts) == 0:
            self.title = "no selected accounts"
        else:
            self.title = "multiple"


class FilterAuthority(Horizontal, CliveWidget):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    class AuthorityFilterReady(Message):
        """Message sent when authority filter is ready to be applied."""

    class Cleared(Message):
        """Message sent when authority filter was restored to default."""

    class SelectedAccountsChanged(Message):
        """Message sent when selected accounts in AccountSelectionList were changed."""

    BORDER_TITLE = "Filter authority"

    def __init__(self, account: TrackedAccount) -> None:
        super().__init__()
        self._account = account

    def compose(self) -> ComposeResult:
        yield AuthorityInput()
        with AccountFilterCollapsible(initial_title=self._account.name):
            yield AccountSelectionList(self._account)
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
    def authority_input(self) -> AuthorityInput:
        return self.query_exactly_one(AuthorityInput)

    @on(AccountSelectionList.SelectionToggled)
    def account_toggled(self, event: AccountSelectionList.SelectionToggled[str]) -> None:
        self.account_filter_collapsible.update_title(event.selection_list.selected)
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
        self.authority_input.clear_validation()
        self.account_selection_list.restore_default()
        self.account_filter_collapsible.restore_title()
        self.collapse_account_filter_collapsible()

    def collapse_account_filter_collapsible(self) -> None:
        self.account_filter_collapsible.collapsed = True

    def _request_authority_filter(self) -> None:
        self.post_message(self.AuthorityFilterReady())
