from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding

from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.widgets.account_managament_reference import AccountManagementReference
from clive.__private.ui.widgets.add_account_container import AddAccountContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult


class AddTrackedAccountDialog(CliveActionDialog):
    CSS_PATH = [get_relative_css_path(__file__)]
    BINDINGS = [Binding("escape,f4", "cancel", "Quit")]
    AUTO_FOCUS = "Input"

    def __init__(self) -> None:
        super().__init__(border_title="Add tracked account", confirm_button_label="Add")
        self._add_account_container = AddAccountContainer(accounts_type="tracked_accounts", show_section_title=False)

    def create_dialog_content(self) -> ComposeResult:
        yield AccountManagementReference()
        yield self._add_account_container

    @on(CliveActionDialog.Confirmed)
    async def save_account(self) -> None:
        is_account_saved = await self._add_account_container.save_account()
        if is_account_saved:
            self.app.pop_screen()
