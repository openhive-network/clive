from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import TabPane

from clive.__private.ui.account_list_management.common.manage_accounts_container import ManageAccountsContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult


class WatchedAccounts(TabPane):
    """TabPane used to add and delete watched accounts."""

    DEFAULT_CSS = """
    WatchedAccounts {
        #input-with-button {
            CliveButton {
                width: 10;
                min-width: 10;
            }
        }
    }
    """

    def __init__(self, title: str) -> None:
        super().__init__(title=title)

    def compose(self) -> ComposeResult:
        yield ManageAccountsContainer(accounts_type="watched_accounts")
