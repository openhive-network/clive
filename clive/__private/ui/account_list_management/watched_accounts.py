from __future__ import annotations

from clive.__private.ui.account_list_management.common.manage_accounts_tab_pane import ManageAccountsTabPane


class WatchedAccounts(ManageAccountsTabPane):
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
        super().__init__(title=title, accounts_type="watched_accounts")
