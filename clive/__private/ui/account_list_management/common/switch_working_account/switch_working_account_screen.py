from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Center, Horizontal, Vertical
from textual.screen import ModalScreen

from clive.__private.ui.account_list_management.account_list_management import AccountListManagement
from clive.__private.ui.account_list_management.common.switch_working_account.switch_working_account_container import (
    SwitchWorkingAccountContainer,
)
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.widgets.buttons.cancel_button import CancelButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton
from clive.__private.ui.widgets.notice import Notice

if TYPE_CHECKING:
    from textual.app import ComposeResult


class SwitchWorkingAccountScreenContent(Vertical):
    BORDER_TITLE = "Switch working account"


class SwitchWorkingAccountScreen(ModalScreen[None]):
    CSS_PATH = [get_relative_css_path(__file__)]
    BINDINGS = [Binding("escape,f3", "cancel", "Quit")]

    AUTO_FOCUS = "RadioSet"

    def __init__(self) -> None:
        super().__init__()
        self._switch_working_account_container = SwitchWorkingAccountContainer(show_title=False)

    def compose(self) -> ComposeResult:
        with SwitchWorkingAccountScreenContent():
            with Vertical(id="notice-container"):
                yield Notice("To add/remove any account to the list, go to:", variant="grey")
                with Center():
                    yield OneLineButton("Account management", id_="account-management-button")
            yield self._switch_working_account_container
            with Horizontal(id="buttons-container"):
                yield OneLineButton("Confirm", variant="success", id_="confirm-button")
                yield CancelButton()

    @on(OneLineButton.Pressed, "#account-management-button")
    def push_account_list_management_screen(self) -> None:
        self.app.push_screen(AccountListManagement())

    @on(OneLineButton.Pressed, "#confirm-button")
    def confirm_selected_working_account(self) -> None:
        self._switch_working_account_container.confirm_selected_working_account()
        self.app.pop_screen()

    @on(CancelButton.Pressed, "#cancel-button")
    def action_cancel(self) -> None:
        self.app.pop_screen()
