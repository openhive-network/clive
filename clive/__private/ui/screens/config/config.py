from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.widgets import Static

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.screens.config.account_management.account_management import AccountManagement
from clive.__private.ui.screens.config.manage_key_aliases import ManageKeyAliases
from clive.__private.ui.screens.config.switch_node_address.switch_node_address import SwitchNodeAddress
from clive.__private.ui.widgets.buttons import CliveButton
from clive.__private.ui.widgets.dialog_container import DialogContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Config(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer():
            yield Static("Please choose which configuration you would like to make:", id="hint")
            yield CliveButton("Select node", id_="select-node")
            yield CliveButton("Manage key aliases", id_="manage-key-aliases")
            yield CliveButton("Accounts management", id_="account-list-management")

    @on(CliveButton.Pressed, "#select-node")
    def push_set_node_address_screen(self) -> None:
        self.app.push_screen(SwitchNodeAddress())

    @on(CliveButton.Pressed, "#account-list-management")
    def push_account_list_management_screen(self) -> None:
        self.app.push_screen(AccountManagement())

    @on(CliveButton.Pressed, "#manage-key-aliases")
    async def push_manage_key_aliases_screen(self) -> None:
        await self.app.push_screen(ManageKeyAliases())

    def _has_working_account(self) -> bool:
        return self.profile.accounts.has_working_account
