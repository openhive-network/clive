from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual import on
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Collapsible, SelectionList
from textual.widgets._selection_list import Selection

from clive.__private.ui.clive_widget import CliveWidget
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

    class SelectionToggled(SelectionList.SelectionToggled[str]):
        selection_list: AccountSelectionList

    class SelectionMessage(SelectionList.SelectionMessage[str]):
        selection_list: AccountSelectionList

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
    def _handle_selection(self, event: AccountSelectionList.SelectionToggled) -> None:
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
        all_option = Selection(self.ALL_OPTION, self.ALL_OPTION, id=self.ALL_OPTION)
        tracked_account_options = [
            Selection(
                self._get_account_selection_prompt(tracked_account.name),
                tracked_account.name,
                initial_state=tracked_account.name == self._initial_checked_account_name,
                id=tracked_account.name,
            )
            for tracked_account in self.profile.accounts.tracked
        ]

        return [all_option, *tracked_account_options]

    def _get_account_selection_prompt(self, account_name: str) -> str:
        postfix = " (working)" if self.profile.accounts.is_account_working(account_name) else ""
        return f"{account_name}{postfix}"


class AccountFilterCollapsible(Collapsible):
    BORDER_TITLE = " Authority for accounts "
    TITLE_NO_SELECTION: Final[str] = "no selected accounts"
    TITLE_MULTIPLE_SELECTION: Final[str] = "multiple"

    def __init__(self, account: TrackedAccount) -> None:
        super().__init__(title=account.name)
        self.compose_add_child(AccountSelectionList(account))
        self._initial_title = account.name

    def restore_title(self) -> None:
        self.title = self._initial_title

    @on(AccountSelectionList.SelectionToggled)
    def update_title(self, event: AccountSelectionList.SelectionToggled) -> None:
        selection_list = event.selection_list
        selected = selection_list.selected
        count = len(selected)

        is_no_selection = count == 0
        is_single_selection = count == 1
        is_all_with_single_account_selected = count == 2 and selection_list.is_all_selected  # noqa: PLR2004

        if is_no_selection:
            self.title = self.TITLE_NO_SELECTION
        elif is_single_selection:
            self.title = selected[0]
        elif is_all_with_single_account_selected:
            self.title = next(name for name in selected if name != selection_list.ALL_OPTION)
        else:
            self.title = self.TITLE_MULTIPLE_SELECTION


class FilterAuthority(Horizontal, CliveWidget):
    DEFAULT_CSS = """
    FilterAuthority {
        border-title-style: bold;
        border-title-color: $text;
        border-title-background: $primary;
        border: $primary outer;
        padding-top: 1;
        width: 6fr;
        height: auto;

        CliveButton {
            width: 1fr;
            min-width: 1fr;
        }

        ClearButton {
            margin: 0 1;
        }

        AuthorityFilterInput {
            width: 9fr;
        }
    }
    """
    BORDER_TITLE = "Filter authority"

    class AuthorityFilterReady(Message):
        """Message sent when authority filter is ready to be applied."""

    class Cleared(Message):
        """Message sent when authority filter was restored to default."""

    def compose(self) -> ComposeResult:
        yield AuthorityFilterInput(title="Authority entry account or public/private key")
        yield SearchButton()
        yield ClearButton()

    @property
    def authority_filter_input(self) -> AuthorityFilterInput:
        return self.query_exactly_one(AuthorityFilterInput)

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

    def _request_authority_filter(self) -> None:
        self.post_message(self.AuthorityFilterReady())


class FilterAuthorityExtended(FilterAuthority):
    """
    Extended version of filter authority with option to filter by specific accounts.

    Attributes:
        DEFAULT_CSS: The default CSS styling for this widget.

    Args:
        account: The account that will be initially selected in the account filter collapsible widget.
    """

    DEFAULT_CSS = """
    FilterAuthorityExtended {
        width: 10fr;

        CliveButton {
            width: 1fr;
            min-width: 1fr;
        }

        ClearButton {
            margin: 0 1;
        }

        AuthorityFilterInput {
            width: 6fr;
        }

        AccountFilterCollapsible {
            border-title-background: $primary;
            border-title-color: $text;
            border-title-style: bold;
            margin-right: 1;
            width: 3fr;

            Contents {
                padding: 1 0 0 0;
            }
        }
    }
    """

    class SelectedAccountsChanged(Message):
        """Message sent when selected accounts in AccountSelectionList were changed."""

    def __init__(self, account: TrackedAccount) -> None:
        super().__init__()
        self._account = account

    def compose(self) -> ComposeResult:
        yield AuthorityFilterInput()
        yield AccountFilterCollapsible(self._account)
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

    @on(AccountSelectionList.SelectionToggled)
    def account_toggled(self) -> None:
        self.post_message(self.SelectedAccountsChanged())

    def apply_default_filter(self) -> None:
        super().apply_default_filter()
        self.account_selection_list.restore_default()
        self.account_filter_collapsible.restore_title()
        self.collapse_account_filter_collapsible()

    def collapse_account_filter_collapsible(self) -> None:
        self.account_filter_collapsible.collapsed = True
