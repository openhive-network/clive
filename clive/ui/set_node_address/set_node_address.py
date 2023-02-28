from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlparse

from textual.binding import Binding
from textual.widgets import Input, Label

from clive.storage.mock_database import NodeAddress
from clive.ui.shared.form_screen import FormScreen
from clive.ui.widgets.big_title import BigTitle

if TYPE_CHECKING:
    from textual.app import ComposeResult


class SetNodeAddress(FormScreen):
    BINDINGS = [Binding("f10", "save_node_address", "Save")]

    def create_main_panel(self) -> ComposeResult:
        yield BigTitle("set node address")
        yield Label("Node address:")
        yield Input(
            str(self.app.profile_data.node_address), placeholder="e.x.: https://api.hive.blog", id="set_node_address"
        )

    def action_save_node_address(self) -> None:
        try:
            url = urlparse(self.get_widget_by_id("set_node_address", expect_type=Input).value)
            self.app.profile_data.node_address = NodeAddress(url.scheme, url.netloc, url.port)
        except ValueError:
            pass
