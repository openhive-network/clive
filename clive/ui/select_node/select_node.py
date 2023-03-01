from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Button, Input, Static, Switch

from clive.storage.mock_database import NodeAddress
from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.clive_widget import CliveWidget
from clive.ui.widgets.select.select import Select
from clive.ui.widgets.select.select_item import SelectItem
from clive.ui.widgets.view_bag import ViewBag

if TYPE_CHECKING:
    from rich.console import RenderableType
    from textual.app import ComposeResult


class ModeSwitch(Switch):
    """A switch that changes the way the node address is selected."""


class SelectedNodeAddress(Static, CliveWidget):
    """The currently selected node address."""

    def render(self) -> RenderableType:
        return f"Selected node address: {self.app.profile_data.node_address}"


class NodesList(Container, CliveWidget):
    def compose(self) -> ComposeResult:
        yield Static("Please select the node you want to connect to from the predefined list below.")
        yield Select(
            items=[SelectItem(node, str(node)) for idx, node in enumerate(self.app.profile_data.backup_node_addresses)],
            selected=self.app.profile_data.node_address,
            list_mount="ViewBag",
        )


class ManualNode(Container, CliveWidget):
    def compose(self) -> ComposeResult:
        yield Static("Please manually enter the node address you want to connect to.")
        yield Input(placeholder=f"e.g.: {self.app.profile_data.node_address}", id="node-address-input")
        yield Button("Save", id="save-node-address-button")


class ModeSwitchContainer(Horizontal):
    def compose(self) -> ComposeResult:
        yield ModeSwitch()
        yield Static("Toggle mode")


class SelectNode(BaseScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__selected_node = SelectedNodeAddress()
        self.__nodes_list = NodesList()
        self.__manual_node = ManualNode(classes="-hidden")

    def create_main_panel(self) -> ComposeResult:
        with ViewBag():
            yield self.__selected_node
            yield Static()
            yield ModeSwitchContainer()
            yield Static()
            yield self.__manual_node
            yield self.__nodes_list

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.selected:
            self.app.profile_data.node_address = event.selected.value
            self.app.profile_data.save()
            self.__selected_node.refresh()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-node-address-button":
            raw_value = self.app.query_one("#node-address-input", Input).value

            with contextlib.suppress(ValueError):
                url = urlparse(raw_value)
            if url.hostname:
                self.app.profile_data.node_address = NodeAddress(url.scheme, str(url.hostname), url.port)
                self.app.profile_data.save()
                self.__selected_node.refresh()

    def on_switch_changed(self) -> None:
        self.__nodes_list.toggle_class("-hidden")
        self.__manual_node.toggle_class("-hidden")
