from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.screens.config.account_management.account_management import AccountManagement
from clive.__private.ui.screens.config.change_bindings import ChangeBindings
from clive.__private.ui.screens.config.manage_key_aliases import ManageKeyAliases
from clive.__private.ui.screens.config.switch_node_address import SwitchNodeAddress
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.buttons import OneLineButton
from clive.__private.ui.widgets.section import Section

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Config(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [
        Binding("escape", "app.go_to_dashboard", "Back to dashboard"),
    ]

    def create_main_panel(self) -> ComposeResult:
        yield BigTitle("Configuration")
        with Section(title="Please choose which configuration you would like to make"):
            yield OneLineButton("Select node", id_="select-node")
            yield OneLineButton("Manage key aliases", id_="manage-key-aliases")
            yield OneLineButton("Accounts management", id_="account-list-management")
            yield OneLineButton("Change bindings", id_="change-bindings")

    @on(OneLineButton.Pressed, "#select-node")
    def push_set_node_address_screen(self) -> None:
        self.app.push_screen(SwitchNodeAddress())

    @on(OneLineButton.Pressed, "#account-list-management")
    def push_account_list_management_screen(self) -> None:
        self.app.push_screen(AccountManagement())

    @on(OneLineButton.Pressed, "#manage-key-aliases")
    async def push_manage_key_aliases_screen(self) -> None:
        await self.app.push_screen(ManageKeyAliases())

    @on(OneLineButton.Pressed, "#change-bindings")
    async def push_change_bindings_aliases_screen(self) -> None:
        await self.app.push_screen(ChangeBindings())
