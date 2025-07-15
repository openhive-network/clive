from __future__ import annotations

from typing import Final

from clive.__private.ui.screens.settings.account_management.common.manage_accounts_tab_pane import ManageAccountsTabPane


class TrackedAccounts(ManageAccountsTabPane):
    """TabPane used to add and delete tracked accounts."""

    DEFAULT_CSS = """
    TrackedAccounts {
        #input-with-button {
            CliveButton {
                width: 10;
                min-width: 10;
            }
        }
    }
    """
    TITLE: Final[str] = "Tracked accounts"

    def __init__(self) -> None:
        super().__init__(title=self.TITLE, accounts_type="tracked_accounts")
