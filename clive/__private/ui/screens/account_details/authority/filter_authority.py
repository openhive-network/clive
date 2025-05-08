from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.widgets import Collapsible, SelectionList
from textual.widgets._selection_list import Selection

from clive.__private.core.accounts.accounts import TrackedAccount
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.widgets.buttons import (
    ClearButton,
    SearchButton,
)
from clive.__private.ui.widgets.inputs.authority_input import AuthorityInput

if TYPE_CHECKING:
    from textual.app import ComposeResult


class AccountFilterCollapsible(Collapsible):
    DEFAULT_CSS = """
    AccountFilterCollapsible {
        border-title-background: $primary;
        border-title-color: $text;
        border-title-style: bold;
        margin-right: 1;
        border-top: $primary panel;
        width: 3fr;

        Contents {
          padding: 1 0 0 0;
        }
      }
    """
    BORDER_TITLE = "Authority for accounts:"

    def __init__(self, accounts: list[TrackedAccount] | list[str]) -> None:
        if isinstance(next(iter(accounts)), TrackedAccount):
            self._initial_checked_accounts = [account.name for account in accounts]
        else:
            self._initial_checked_accounts = accounts

        super().__init__(title="temporary title")  # title can't be set before calling super().__init__()
        self._initial_title = self.update_title(self._initial_checked_accounts)

    def restore_title(self) -> None:
        self.title = self._initial_title

    def update_title(self, selected_accounts: list[str]) -> str:
        if len(selected_accounts) == 1:
            title = next(iter(selected_accounts))
        elif len(selected_accounts) == 0:
            title = "no selected accounts"
        else:
            title = "multiple"
        self.title = title
        return title


class AccountSelectionList(SelectionList[str], CliveWidget):
    """Selection list with account names for filtering authorities."""

    def __init__(self, *, accounts: list[TrackedAccount] | list[str]) -> None:
        if isinstance(next(iter(accounts)), TrackedAccount):
            self._initial_checked_accounts = [account.name for account in accounts]
        else:
            self._initial_checked_accounts = accounts
        working_account_name = self.profile.accounts.working.name
        self._filter_entries = [Selection("all", "all")] + [
            Selection(
                f"{tracked_account.name}{
                    ' (working)' if working_account_name and tracked_account.name is working_account_name else ''
                }",
                tracked_account.name,
                initial_state=tracked_account.name in self._initial_checked_accounts,
            )
            for tracked_account in self.profile.accounts.tracked
        ]
        super().__init__(*self._filter_entries)

    def restore_default(self) -> None:
        self.deselect_all()
        all_selections = [self.get_option_at_index(index) for index in range(len(self.profile.accounts.tracked) + 1)]
        for selection in all_selections:
            if selection.value in self._initial_checked_accounts:
                self.select(selection)


class FilterAuthority(Horizontal, CliveWidget):
    DEFAULT_CSS = """
    FilterAuthority {
      border-title-style: bold;
      border-title-color: $text;
      border-title-background: $primary;
      border: $primary outer;
      padding-top: 1;
      width: 10fr;
      height: auto;

      CliveButton {
        width: 1fr;
        min-width: 1fr;
      }

      ClearButton {
        margin: 0 1;
      }

      AuthorityInput {
        width: 6fr;
      }
    }
    """
    BORDER_TITLE = "Filter authority"

    def __init__(self, *, accounts: list[TrackedAccount] | list[str]) -> None:
        super().__init__()
        self._accounts = accounts

    def compose(self) -> ComposeResult:
        yield AuthorityInput()
        with AccountFilterCollapsible(accounts=self._accounts):
            yield AccountSelectionList(accounts=self._accounts)
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

    def collapse_account_filter_collapsible(self) -> None:
        self.account_filter_collapsible.collapsed = True

    def apply_default_filter(self) -> None:
        self.authority_input.clear_validation()
        self.account_selection_list.restore_default()
        self.account_filter_collapsible.restore_title()
        self.collapse_account_filter_collapsible()
