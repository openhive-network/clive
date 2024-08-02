from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Center, Container, Horizontal
from textual.screen import ModalScreen

from clive.__private.ui.account_list_management.common.account_managament_reference import AccountManagementReference
from clive.__private.ui.account_list_management.common.add_account_container import AddAccountContainer
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton

if TYPE_CHECKING:
    from textual.app import ComposeResult


class AddTrackedAccountScreenContent(Container):
    BORDER_TITLE = "Add tracked account"


class AddTrackedAccountScreen(ModalScreen[None]):
    CSS_PATH = [get_relative_css_path(__file__)]
    BINDINGS = [Binding("escape,f4", "cancel", "Quit")]
    AUTO_FOCUS = "Input"

    def __init__(self) -> None:
        super().__init__()
        self._add_account_container = AddAccountContainer(accounts_type="tracked_accounts", show_section_title=False)

    def compose(self) -> ComposeResult:
        with AddTrackedAccountScreenContent():
            yield AccountManagementReference()
            yield self._add_account_container
            with Center(), Horizontal(id="buttons-container"):
                yield OneLineButton(
                    "Add",
                    variant="success",
                    id_="save-account-button",
                )
                yield OneLineButton(
                    "Cancel",
                    variant="error",
                    id_="cancel-button",
                )

    @on(OneLineButton.Pressed, "#cancel-button")
    def action_cancel(self) -> None:
        self.app.pop_screen()

    @on(OneLineButton.Pressed, "#save-account-button")
    async def save_account(self) -> None:
        await self._add_account_container.save_account()
        self.app.pop_screen()
