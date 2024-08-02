from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import TabPane

from clive.__private.ui.account_list_management.common.add_account_container import AddAccountContainer
from clive.__private.ui.account_list_management.common.manage_accounts_table import AccountsType, ManageAccountsTable
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.scrolling import ScrollablePart

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ManageAccountsTabPane(TabPane, CliveWidget):
    """TabPane used to add and delete watched or known accounts."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: str, accounts_type: AccountsType) -> None:
        super().__init__(title=title)
        self._accounts_type = accounts_type
        self._add_account_container = AddAccountContainer(accounts_type)

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            yield self._add_account_container
            yield ManageAccountsTable(self._accounts_type)
