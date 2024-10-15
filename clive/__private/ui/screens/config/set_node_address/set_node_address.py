from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Select, Static
from textual.widgets._select import NoSelection

from clive.__private.core.url import Url
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.section import SectionScrollable
from clive.exceptions import NodeAddressError

if TYPE_CHECKING:
    from rich.console import RenderableType
    from textual.app import ComposeResult


class NodeSelector(Select[Url], CliveWidget):
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

    async def _valid_and_save_address(self) -> None:
        address = self.query_exactly_one(NodeSelector).value
        assert not isinstance(address, NoSelection), "No node was selected."
        await self.node.set_address(address)
        self.app.trigger_node_watchers()

    async def save_node_address_with_gui_support(self) -> None:
        try:
            await self._valid_and_save_address()
        except NodeAddressError:
            self.notify(
                "Invalid node address. Please enter it in a valid format (e.g. https://api.hive.blog)",
                severity="error",
            )
        else:
            self.notify(f"Node address set to `{self.node.address}`.")


class SetNodeAddressBase(BaseScreen, ABC):
    CSS_PATH = [get_relative_css_path(__file__)]

    def create_main_panel(self) -> ComposeResult:
        # Section is focusable bcs it's not possible to use scrolling via keyboard when Select is focused
        with SectionScrollable("Set node address", focusable=True):
            yield SelectedNodeAddress()
            yield NodesList()

    @on(NodeSelector.Changed)
    async def update_selected_node_address(self) -> None:
        self.query_one(SelectedNodeAddress).refresh()
        await self.query_one(NodesList).save_node_address_with_gui_support()


class SetNodeAddress(SetNodeAddressBase):
    BIG_TITLE = "configuration"
    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]
