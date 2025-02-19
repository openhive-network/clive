from __future__ import annotations

from typing import TYPE_CHECKING

from helpy import HttpUrl
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Static

from clive.__private.core.node import Node
from clive.__private.core.profile import Profile
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.widgets.clive_basic.clive_select import CliveSelect

if TYPE_CHECKING:
    from rich.console import RenderableType
    from textual.app import ComposeResult


class SelectedNodeAddress(Static):
    """The currently selected node address."""

    node_address: HttpUrl | None = reactive(None)  # type: ignore[assignment]

    def __init__(self, node_address: HttpUrl) -> None:
        super().__init__()
        self.node_address = node_address

    def render(self) -> RenderableType:
        return f"Selected node address: {self.node_address}"


class NodeSelector(CliveSelect[HttpUrl], CliveWidget):
    """Select for the node address."""

    def __init__(self) -> None:
        super().__init__(
            [(str(url), url) for url in self.profile.backup_node_addresses],
            allow_blank=False,
            value=self.node.http_endpoint,
        )


class NodesList(Container, CliveWidget):
    """Container for the list of nodes to choose with method to save given address."""

    DEFAULT_CSS = """
    NodesList {
        height: auto;
    }
    """

    def __init__(self, node: Node) -> None:
        super().__init__()
        self._node = node

    def compose(self) -> ComposeResult:
        yield Static("Please select the node you want to connect to from the predefined list below.")
        with self.prevent(NodeSelector.Changed):
            yield NodeSelector()

    async def save_selected_node_address(self) -> bool:
        async def set_address(address: HttpUrl) -> None:
            await self.node.set_address(address)
            self.app.trigger_node_watchers()
            self.notify(f"Node address set to `{address}`.")

        new_address = self.query_exactly_one(NodeSelector).value_ensure
        temp_profile = Profile.create("temporary", node_address=new_address)

        async with Node(temp_profile) as temp_node:
            is_new_node_online = await temp_node.cached.online
            new_network_type = temp_node.cached.network_type_or_none

        if not is_new_node_online:
            self.notify("Cannot connect to an offline node.", severity="error")
            return False

        is_current_node_online = await self.node.cached.online
        current_network_type = self.node.cached.network_type_or_none

        if not is_current_node_online or new_network_type == current_network_type:
            # When we have no connection, just set the address without comparing network types.
            # When both nodes are online and have the same network type, we can just switch the address.
            await set_address(new_address)
            return True

        # block possibility to stay connected to node with different network type
        self.notify("Cannot connect to a node with a different network type.", severity="error")
        return False
