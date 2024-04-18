from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from textual import on
from textual.widgets import Static

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

AccountsType = Literal["known_accounts", "watched_accounts"]


class AccountRow(CliveCheckerboardTableRow):
    def __init__(self, account: Account, account_type: AccountsType) -> None:
        super().__init__(
            CliveCheckerBoardTableCell(account.name),
            CliveCheckerBoardTableCell(
                OneLineButton(
                    "Mark as unknown" if account_type == "known_accounts" else "Unwatch",
                    variant="error",
                    id_="discard-account-button",
                )
            ),
        )
        self._account = account
        self._account_type = account_type

    @on(CliveButton.Pressed, "#discard-account-button")
    def discard_account(self) -> None:
        getattr(self.app.world.profile_data, self._account_type).discard(self._account)
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

        #manage-accounts-title {
            text-style: bold;
            background: $primary;
            width: 1fr;
        }
    }
    """

    ATTRIBUTE_TO_WATCH = "profile_data"

    def __init__(self, accounts_type: AccountsType) -> None:
        super().__init__(
            Static(
                f"Your {self.remove_underscore_from_text(accounts_type)}",
                id="manage-accounts-title",
            ),
            AccountsTableHeader(),
        )
        self._previous_accounts: set[Account] | NotUpdatedYet = NotUpdatedYet()
        self._accounts_type = accounts_type

    def create_dynamic_rows(self, content: ProfileData) -> list[AccountRow]:
        return [
            AccountRow(account, self._accounts_type) for account in getattr(content, f"{self._accounts_type}_sorted")
        ]

    def get_no_content_available_widget(self) -> Static:
        return NoContentAvailable(
            f"You have no {self.remove_underscore_from_text(self._accounts_type)}",
        )

    def check_if_should_be_updated(self, content: ProfileData) -> bool:
        return getattr(content, self._accounts_type) != self._previous_accounts  # type: ignore[no-any-return]

    def is_anything_to_display(self, content: ProfileData) -> bool:
        return len(getattr(content, self._accounts_type)) != 0

    @property
    def object_to_watch(self) -> TextualWorld:
        return self.app.world

    def update_previous_state(self, content: ProfileData) -> None:
        self._previous_accounts = getattr(content, self._accounts_type).copy()

    def remove_underscore_from_text(self, text: str) -> str:
        return text.replace("_", " ")
