from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual import on
from textual.binding import Binding

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.node_widgets import NodeSelector, NodesList, SelectedNodeAddress
from clive.__private.ui.widgets.section import SectionScrollable

if TYPE_CHECKING:
    from textual.app import ComposeResult


class SetNodeAddress(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]
    BIG_TITLE = "configuration"
    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._node = self.get_node()

    def create_main_panel(self) -> ComposeResult:
        # Section is focusable bcs it's not possible to use scrolling via keyboard when Select is focused
        with SectionScrollable("Set node address", focusable=True):
            yield SelectedNodeAddress(self._node.address)
            yield NodesList(self._node)

    @on(NodeSelector.Changed)
    async def save_selected_node_address(self) -> None:
        self.query_exactly_one(SelectedNodeAddress).node_address = self.query_exactly_one(NodeSelector).value_ensure
        await self.query_exactly_one(NodesList).save_selected_node_address()
