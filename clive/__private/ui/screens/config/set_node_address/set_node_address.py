from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any

from textual import on
from textual.binding import Binding
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Static

from clive.__private.core.url import Url
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.clive_basic.clive_select import CliveSelect
from clive.__private.ui.widgets.section import SectionScrollable

if TYPE_CHECKING:
    from rich.console import RenderableType
    from textual.app import ComposeResult

    from clive.__private.core.node import Node


class NodeSelector(CliveSelect[Url], CliveWidget):
    """Select for the node address."""

    def __init__(self) -> None:
        super().__init__(
            [(str(url), url) for url in self.profile.backup_node_addresses],
            allow_blank=False,
            value=self.node.address,
        )


class SelectedNodeAddress(Static):
    """The currently selected node address."""

    node_address: Url | None = reactive(None)  # type: ignore[assignment]

    def __init__(self, node_address: Url) -> None:
        super().__init__()
        self.node_address = node_address

    def render(self) -> RenderableType:
        return f"Selected node address: {self.node_address}"


class NodesList(Container):
    def compose(self) -> ComposeResult:
        yield Static("Please select the node you want to connect to from the predefined list below.")
        with self.prevent(NodeSelector.Changed):
            yield NodeSelector()


class SetNodeAddressBase(BaseScreen, ABC):
    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._node = self.get_node()

    def create_main_panel(self) -> ComposeResult:
        # Section is focusable bcs it's not possible to use scrolling via keyboard when Select is focused
        with SectionScrollable("Set node address", focusable=True):
            yield SelectedNodeAddress(self._node.address)
            yield NodesList()

    @on(NodeSelector.Changed)
    async def save_selected_node_address(self) -> None:
        address = self.query_exactly_one(NodeSelector).value_ensure
        await self._node.set_address(address)
        self.app.trigger_node_watchers()
        self.query_exactly_one(SelectedNodeAddress).node_address = address
        self.notify(f"Node address set to `{self._node.address}`.")

    def get_node(self) -> Node:
        """Override this method if widget should operate on node other than node from the world."""
        return self.world.node


class SetNodeAddress(SetNodeAddressBase):
    BIG_TITLE = "configuration"
    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]
