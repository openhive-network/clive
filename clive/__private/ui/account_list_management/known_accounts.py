from __future__ import annotations

from clive.__private.ui.account_list_management.common.manage_accounts_tab_pane import ManageAccountsTabPane


class KnownAccounts(ManageAccountsTabPane):
    """TabPane used to add and delete known accounts."""

    def __init__(self, title: str):
        super().__init__(title=title, accounts_type="known_accounts")
