from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any

from textual import on
from textual.binding import Binding
from textual.containers import Container
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


class NodeSelector(CliveSelect[Url], CliveWidget):
    """Select for the node address."""

    def __init__(self) -> None:
        super().__init__(
            [(str(url), url) for url in self.profile.backup_node_addresses],
            allow_blank=False,
            value=self.node.address,
        )


class SelectedNodeAddress(Static, CliveWidget):
    """The currently selected node address."""

    def render(self) -> RenderableType:
        return f"Selected node address: {self.node.address}"


class NodesList(Container, CliveWidget):
    def compose(self) -> ComposeResult:
        yield Static("Please select the node you want to connect to from the predefined list below.")
        with self.prevent(NodeSelector.Changed):
            yield NodeSelector()


class SetNodeAddressBase(BaseScreen, ABC):
    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.__selected_node = SelectedNodeAddress()
        self.__nodes_list = NodesList()

    def create_main_panel(self) -> ComposeResult:
        # Section is focusable bcs it's not possible to use scrolling via keyboard when Select is focused
        with SectionScrollable("Set node address", focusable=True):
            yield self.__selected_node
            yield self.__nodes_list

    async def _valid_and_save_address(self) -> None:
        address = self.query_exactly_one(NodeSelector).value_ensure
        await self.node.set_address(address)
        self.app.trigger_node_watchers()
        self.__selected_node.refresh()

    @on(NodeSelector.Changed)
    async def save_node_address_with_gui_support(self) -> None:
        await self._valid_and_save_address()
        self.notify(f"Node address set to `{self.node.address}`.")


class SetNodeAddress(SetNodeAddressBase):
    BIG_TITLE = "configuration"
    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]
