from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from textual import on

from clive.__private.ui.account_list_management.common.header_of_tables import AccountsTableHeader
from clive.__private.ui.not_updated_yet import NotUpdatedYet
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_checkerboard_table import (
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.no_content_available import NoContentAvailable
from clive.__private.ui.widgets.one_line_button import OneLineButton

if TYPE_CHECKING:
    from clive.__private.core.profile_data import ProfileData
    from clive.__private.core.world import TextualWorld
    from clive.__private.storage.accounts import Account
from clive.__private.storage.accounts import WorkingAccount

AccountsType = Literal["known_accounts", "tracked_accounts"]


class AccountRow(CliveCheckerboardTableRow):
    def __init__(self, account: Account, account_type: AccountsType) -> None:
        self._is_working_account = isinstance(account, WorkingAccount)
        self._account = account
        self._account_type = account_type
        super().__init__(*self._create_cells())

    def _create_cells(self) -> list[CliveCheckerBoardTableCell]:
        cells_unfiltered = [
            CliveCheckerBoardTableCell(self._account.name),
            self._create_account_type_column() if self._account_type == "tracked_accounts" else None,
            CliveCheckerBoardTableCell(
                OneLineButton(
                    "Remove",
                    variant="error",
                    id_="discard-account-button",
                )
            ),
        ]
        return list(filter(None, cells_unfiltered))

    def _create_account_type_column(self) -> CliveCheckerBoardTableCell:
        return CliveCheckerBoardTableCell("working" if self._is_working_account else "watched")

    @on(CliveButton.Pressed, "#discard-account-button")
    def discard_account(self) -> None:
        if self._account_type == "known_accounts":
            self.profile_data.known_accounts.discard(self._account)
        else:
            self.profile_data.remove_tracked_account(self._account)
        self.app.trigger_profile_data_watchers()


class ManageAccountsTable(CliveCheckerboardTable):
    """Common table for a known and watched accounts."""

    DEFAULT_CSS = """
    ManageAccountsTable {
        margin-top: 1;
        width: 50%;

        Static {
            text-align: center;
        }

        CliveButton {
            width: 1fr;
        }
    }
    """

    ATTRIBUTE_TO_WATCH = "profile_data"

    def __init__(self, accounts_type: AccountsType) -> None:
        super().__init__(
            header=AccountsTableHeader(show_type_column=accounts_type == "tracked_accounts"),
            title=f"Your {self.remove_underscore_from_text(accounts_type)}",
        )
        self._previous_accounts: set[Account] | NotUpdatedYet = NotUpdatedYet()
        self._accounts_type = accounts_type

    def create_dynamic_rows(self, content: ProfileData) -> list[AccountRow]:
        return [
            AccountRow(account, self._accounts_type) for account in getattr(content, f"{self._accounts_type}_sorted")
        ]

    def get_no_content_available_widget(self) -> NoContentAvailable:
        return NoContentAvailable(
            f"You have no {self.remove_underscore_from_text(self._accounts_type)}",
        )

    def check_if_should_be_updated(self, content: ProfileData) -> bool:
        actual_accounts = self._get_accounts_from_new_content(content)
        return actual_accounts != self._previous_accounts

    def is_anything_to_display(self, content: ProfileData) -> bool:
        return (
            content.has_known_accounts() if self._accounts_type == "known_accounts" else content.has_tracked_accounts()
        )

    @property
    def object_to_watch(self) -> TextualWorld:
        return self.world

    def update_previous_state(self, content: ProfileData) -> None:
        self._previous_accounts = self._get_accounts_from_new_content(content)

    def _get_accounts_from_new_content(self, content: ProfileData) -> set[Account]:
        return (
            content.known_accounts.copy()
            if self._accounts_type == "known_accounts"
            else content.get_tracked_accounts().copy()
        )

    def remove_underscore_from_text(self, text: str) -> str:
        return text.replace("_", " ")
