from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.widgets import Input, Label

from clive.ui.shared.form_screen import FormScreen
from clive.ui.widgets.big_title import BigTitle
from clive.ui.widgets.view_bag import ViewBag

if TYPE_CHECKING:
    from textual.app import ComposeResult


class SetAccount(FormScreen):
    BINDINGS = [Binding("f10", "save_account_name", "Save")]

    def create_main_panel(self) -> ComposeResult:
        yield ViewBag(
            BigTitle("set account name"),
            Label("Account name:\t @"),
            Input(
                str(self.app.profile_data.active_account.name),
                placeholder="e.x.: cookingwithkasia",
                id="set_account_name",
            ),
        )

    def action_save_account_name(self) -> None:
        self.app.profile_data.active_account.name = self.get_widget_by_id("set_account_name", expect_type=Input).value
