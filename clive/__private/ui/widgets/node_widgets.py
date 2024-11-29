from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Static

from clive.__private.core.url import Url
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.widgets.clive_basic.clive_select import CliveSelect

if TYPE_CHECKING:
    from rich.console import RenderableType
    from textual.app import ComposeResult

    from clive.__private.core.node import Node


class SelectedNodeAddress(Static):
    """The currently selected node address."""

    node_address: Url | None = reactive(None)  # type: ignore[assignment]

    def __init__(self, node_address: Url) -> None:
        super().__init__()
        self.node_address = node_address

    def render(self) -> RenderableType:
        return f"Selected node address: {self.node_address}"


class NodeSelector(CliveSelect[Url], CliveWidget):
    """Select for the node address."""

    def __init__(self) -> None:
        super().__init__(
            [(str(url), url) for url in self.profile.backup_node_addresses],
            allow_blank=False,
            value=self.node.address,
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

    async def save_selected_node_address(self) -> None:
        address = self.query_exactly_one(NodeSelector).value_ensure
        await self._node.set_address(address)
        self.app.trigger_node_watchers()
        self.notify(f"Node address set to `{self._node.address}`.")
