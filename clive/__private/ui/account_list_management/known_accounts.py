from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import TabPane

from clive.__private.ui.account_list_management.common.manage_accounts_container import ManageAccountsContainer
from clive.__private.ui.widgets.scrolling import ScrollablePart

if TYPE_CHECKING:
    from textual.app import ComposeResult


class KnownAccounts(TabPane):
    """TabPane used to add and delete known accounts."""

    def __init__(self, title: str) -> None:
        super().__init__(title=title)

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            yield ManageAccountsContainer(accounts_type="known_accounts")
