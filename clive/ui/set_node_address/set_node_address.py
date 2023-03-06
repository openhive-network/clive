from __future__ import annotations

import contextlib
from datetime import datetime
from typing import TYPE_CHECKING, Final
from urllib.parse import urlparse

import requests
from rich.highlighter import Highlighter
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Button, Input, Static, Switch

from clive.storage.mock_database import NodeAddress
from clive.ui.shared.base_screen import BaseScreen
from clive.ui.shared.form_screen import FormScreen
from clive.ui.widgets.big_title import BigTitle
from clive.ui.widgets.clive_widget import CliveWidget
from clive.ui.widgets.select.select import Select
from clive.ui.widgets.select.select_item import SelectItem
from clive.ui.widgets.view_bag import ViewBag

if TYPE_CHECKING:
    from rich.console import RenderableType
    from rich.text import Text
    from textual import Logger
    from textual.app import ComposeResult


class Body(Static):
    """All the content of the screen, excluding the title"""


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


class NodeUrlHighlighter(Highlighter):
    def __init__(self, logger: Logger) -> None:
        self.logger = logger
        self.__last_highlight_time = datetime.now()
        self.__last_style = "white"
        super().__init__()

    def __check_and_update_highlight_period(self) -> bool:
        highlight_period: Final[int] = 1
        now = datetime.now()
        if (now - self.__last_highlight_time).seconds >= highlight_period:
            self.__last_highlight_time = now
            return True
        return False

    def is_valid_url(self, url: str) -> bool:
        ok_status: Final[int] = 200
        with contextlib.suppress(requests.exceptions.RequestException):
            return (
                requests.post(
                    url,
                    data='{"jsonrpc":"2.0", "method":"condenser_api.get_config", "params":[], "id":1}',
                    headers={"Content-Type": "application/json"},
                    timeout=0.5,
                ).status_code
                == ok_status
            )
        return False

    def highlight(self, text: Text) -> None:
        if self.__check_and_update_highlight_period():
            if self.is_valid_url(str(text)):
                self.__last_style = "green"
            else:
                self.__last_style = "red"
        text.stylize(self.__last_style)


class ManualNode(Container, CliveWidget):
    def compose(self) -> ComposeResult:
        yield Static("Please manually enter the node address you want to connect to.")
        yield Input(
            placeholder=f"e.g.: {self.app.profile_data.node_address}",
            id="node-address-input",
            highlighter=NodeUrlHighlighter(self.log),
        )
        yield Button("Save", id="save-node-address-button")


class ModeSwitchContainer(Horizontal):
    def compose(self) -> ComposeResult:
        yield ModeSwitch()
        yield Static("Toggle mode")


class SetNodeAddressBase(BaseScreen):
    def __init__(self) -> None:
        super().__init__()

        self.__selected_node = SelectedNodeAddress()
        self.__nodes_list = NodesList()
        self.__manual_node = ManualNode(classes="-hidden")

    def create_main_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("set node address")
            with Body():
                yield self.__selected_node
                yield Static()
                yield ModeSwitchContainer()
                yield Static()
                yield self.__nodes_list
                yield self.__manual_node

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.selected:
            self.app.profile_data.node_address = event.selected.value
            self.app.profile_data.save()
            self.__selected_node.refresh()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-node-address-button":
            self.action_save_node_address()

    def action_save_node_address(self) -> None:
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


class SetNodeAddressForm(SetNodeAddressBase, FormScreen):
    BINDINGS = [Binding("f10", "save_node_address", "Save")]


class SetNodeAddress(SetNodeAddressBase):
    BINDINGS = [Binding("escape", "pop_screen", "Cancel")]
