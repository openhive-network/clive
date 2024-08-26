from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.widgets import Static

from clive.__private.ui.account_management.account_management import AccountManagement
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.manage_key_aliases import ManageKeyAliases
from clive.__private.ui.set_node_address.set_node_address import SetNodeAddress
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.clive_screen import CliveScreen, OnlyInUnlockedModeError
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
        self.app.push_screen(SetNodeAddress())

    @on(CliveButton.Pressed, "#account-list-management")
    def push_account_list_management_screen(self) -> None:
        self.app.push_screen(AccountManagement())

    @CliveScreen.try_again_after_unlock
    @on(CliveButton.Pressed, "#manage-key-aliases")
    async def push_manage_key_aliases_screen(self) -> None:
        if not self._has_working_account():
            self.notify("Cannot manage key aliases without working account", severity="error")
            return

        if not self.app_state.is_unlocked:
            raise OnlyInUnlockedModeError

        await self.app.push_screen(ManageKeyAliases())

    def _has_working_account(self) -> bool:
        return self.profile.accounts.has_working_account
