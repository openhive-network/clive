from __future__ import annotations

from typing import Final

from clive.__private.ui.screens.settings.account_management.common.manage_accounts_tab_pane import ManageAccountsTabPane


class KnownAccounts(ManageAccountsTabPane):
    """
    TabPane used to add and delete known accounts.

    Attributes:
        TITLE: Title of the tab pane.
    """

    TITLE: Final[str] = "Known accounts"

    def __init__(self) -> None:
        super().__init__(title=self.TITLE, accounts_type="known_accounts")
