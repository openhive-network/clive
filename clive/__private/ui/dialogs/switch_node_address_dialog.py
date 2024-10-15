from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on

from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.config.set_node_address.set_node_address import NodesList
from clive.__private.ui.widgets.buttons import ConfirmButton
from clive.__private.ui.widgets.section import Section

if TYPE_CHECKING:
    from textual.app import ComposeResult


class SwitchNodeAddressDialog(CliveActionDialog):
    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self) -> None:
        super().__init__(border_title="Switch node address", confirm_button_label="Switch node address")

    def create_dialog_content(self) -> ComposeResult:
        with Section():
            yield NodesList()

    @on(ConfirmButton.Pressed)
    async def switch_node_address(self) -> None:
        await self.query_one(NodesList).save_node_address_with_gui_support()
        self.app.pop_screen()
