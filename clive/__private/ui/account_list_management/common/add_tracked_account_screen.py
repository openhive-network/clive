from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen

from clive.__private.ui.account_list_management.common.account_managament_reference import AccountManagementReference
from clive.__private.ui.account_list_management.common.add_account_container import AddAccountContainer
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.widgets.buttons.clive_button import CliveButton

if TYPE_CHECKING:
    from textual.app import ComposeResult


class AddTrackedAccountScreenContent(Container):
    BORDER_TITLE = "Add tracked account"


class AddTrackedAccountScreen(ModalScreen[None]):
    CSS_PATH = [get_relative_css_path(__file__)]
    BINDINGS = [Binding("escape,f4", "cancel", "Quit")]
    AUTO_FOCUS = "Input"

    def compose(self) -> ComposeResult:
        with AddTrackedAccountScreenContent():
            yield AccountManagementReference()
            yield AddAccountContainer(
                accounts_type="tracked_accounts",
                with_cancel_button=True,
                show_section_title=False,
                use_one_line_buttons=True,
            )

    @on(CliveButton.Pressed, "#cancel-button")
    def action_cancel(self) -> None:
        self.app.pop_screen()
