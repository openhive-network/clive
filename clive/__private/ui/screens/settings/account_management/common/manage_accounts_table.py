from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from textual import on

from clive.__private.ui.not_updated_yet import NotUpdatedYet
from clive.__private.ui.screens.settings.account_management.common.header_of_tables import AccountsTableHeader
from clive.__private.ui.widgets.buttons import CliveButton, OneLineButton
from clive.__private.ui.widgets.clive_basic import (
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from clive.__private.core.accounts.accounts import Account, KnownAccount, TrackedAccount
    from clive.__private.core.profile import Profile
    from clive.__private.core.world import TUIWorld
from clive.__private.core.accounts.accounts import WorkingAccount

AccountsType = Literal["known_accounts", "tracked_accounts"]


def remove_underscore_from_text(text: str) -> str:
    return text.replace("_", " ")


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
            self.profile.accounts.known.remove(self._account)
        else:
            self.profile.accounts.remove_tracked_account(self._account)
        self.app.trigger_profile_watchers()


class ManageAccountsTable(CliveCheckerboardTable):
    """
    Common table for a known and watched accounts.

    Attributes:
        DEFAULT_CSS: Default CSS for the manage accounts table.
        ATTRIBUTE_TO_WATCH: Attribute to watch for updates.
        NO_CONTENT_TEXT: Text to display when there are no accounts.

    Args:
        accounts_type: Type of accounts to manage (known or tracked).
    """

    DEFAULT_CSS = """
    ManageAccountsTable {
        Static {
            text-align: center;
        }

        CliveButton {
            width: 1fr;
        }
    }
    """

    ATTRIBUTE_TO_WATCH = "profile_reactive"
    NO_CONTENT_TEXT = "You have no accounts"

    def __init__(self, accounts_type: AccountsType) -> None:
        super().__init__(
            header=AccountsTableHeader(show_type_column=accounts_type == "tracked_accounts"),
            title=f"Your {remove_underscore_from_text(accounts_type)}",
        )
        self._previous_accounts: list[KnownAccount] | list[TrackedAccount] | NotUpdatedYet = NotUpdatedYet()
        self._accounts_type = accounts_type

    def create_dynamic_rows(self, content: Profile) -> list[AccountRow]:
        if self._accounts_type == "known_accounts":
            accounts: Iterable[Account] = content.accounts.known
        else:
            accounts = content.accounts.tracked
        return [AccountRow(account, self._accounts_type) for account in accounts]

    def check_if_should_be_updated(self, content: Profile) -> bool:
        actual_accounts = self._get_accounts_from_new_content(content)
        return actual_accounts != self._previous_accounts

    def is_anything_to_display(self, content: Profile) -> bool:
        return (
            content.accounts.has_known_accounts
            if self._accounts_type == "known_accounts"
            else content.accounts.has_tracked_accounts
        )

    @property
    def object_to_watch(self) -> TUIWorld:
        return self.world

    def update_previous_state(self, content: Profile) -> None:
        self._previous_accounts = self._get_accounts_from_new_content(content)

    def _get_accounts_from_new_content(self, content: Profile) -> list[KnownAccount] | list[TrackedAccount]:
        return content.accounts.known.content if self._accounts_type == "known_accounts" else content.accounts.tracked
