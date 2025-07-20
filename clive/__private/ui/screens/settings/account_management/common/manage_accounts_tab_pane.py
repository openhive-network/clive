from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Center
from textual.widgets import TabPane

from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.screens.settings.account_management.common.manage_accounts_table import (
    AccountsType,
    ManageAccountsTable,
)
from clive.__private.ui.widgets.add_account_container import AddAccountContainer
from clive.__private.ui.widgets.buttons import AddButton
from clive.__private.ui.widgets.inputs.clive_input import CliveInput
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section import SectionBody

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ManageAccountsTabPane(TabPane, CliveWidget):
    """
    TabPane used to add and delete watched or known accounts.

    Attributes:
        DEFAULT_CSS: Default CSS for the manage accounts tab pane.

    Args:
        title: Title of the tab pane.
        accounts_type: Type of accounts to manage.
    """

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: str, accounts_type: AccountsType) -> None:
        super().__init__(title=title)
        self._accounts_type = accounts_type
        self._add_account_container = AddAccountContainer(accounts_type)

    def compose(self) -> ComposeResult:
        with Center():
            yield self._add_account_container
            with ScrollablePart():
                yield ManageAccountsTable(self._accounts_type)

    def on_mount(self) -> None:
        self._add_account_container.query_exactly_one(SectionBody).mount(AddButton())

    @on(CliveInput.Submitted)
    @on(AddButton.Pressed)
    async def track_account(self) -> None:
        await self._add_account_container.save_account()
