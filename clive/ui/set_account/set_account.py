from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.widgets import Input, Label

from clive.ui.shared.form_screen import FormScreen
from clive.ui.widgets.big_title import BigTitle

if TYPE_CHECKING:
    from textual.app import ComposeResult


class SetAccount(FormScreen):
    BINDINGS = [Binding("f10", "save_account_name", "Save")]

    def create_main_panel(self) -> ComposeResult:
        yield BigTitle("set account name")
        yield Label("Account name:\t @")
        yield Input(
            str(self.app.profile_data.active_account.name), placeholder="e.x.: cookingwithkasia", id="set_account_name"
        )

    def action_save_account_name(self) -> None:
        self.app.profile_data.active_account.name = self.get_widget_by_id("set_account_name", expect_type=Input).value
