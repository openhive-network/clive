from __future__ import annotations

import contextlib
from datetime import datetime
from typing import TYPE_CHECKING, Any, Final

import httpx
from rich.highlighter import Highlighter
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Button, Input, Static, Switch

from clive.__private.storage.contextual import Contextual, ContextualHolder
from clive.__private.storage.mock_database import NodeAddress, ProfileData
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.shared.form_screen import FormScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.notification import Notification
from clive.__private.ui.widgets.select.select import Select
from clive.__private.ui.widgets.select.select_item import SelectItem
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.exceptions import NodeAddressError

if TYPE_CHECKING:
    from rich.console import RenderableType
    from rich.text import Text
    from textual import Logger
    from textual.app import ComposeResult

    from clive.__private.ui.shared.form import Form


class Body(Static):
    """All the content of the screen, excluding the title"""


class ModeSwitch(Switch):
    """A switch that changes the way the node address is selected."""


class SelectedNodeAddress(ContextualHolder[ProfileData], Static, CliveWidget):
    """The currently selected node address."""

    def render(self) -> RenderableType:
        return f"Selected node address: {self.context.node_address}"


class NodesList(ContextualHolder[ProfileData], Container, CliveWidget):
    def compose(self) -> ComposeResult:
        yield Static("Please select the node you want to connect to from the predefined list below.")
        yield Select(
            items=[SelectItem(node, str(node)) for idx, node in enumerate(self.context.backup_node_addresses)],
            selected=self.context.node_address,
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
        with contextlib.suppress(httpx.HTTPError):
            return (
                httpx.post(
                    url,
                    data={"jsonrpc": "2.0", "method": "condenser_api.get_config", "params": [], "id": 1},
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
        yield CliveButton("Save", id_="save-node-address-button")


class ModeSwitchContainer(Horizontal):
    def compose(self) -> ComposeResult:
        yield ModeSwitch()
        yield Static("Toggle mode")


class SetNodeAddressBase(BaseScreen, Contextual[ProfileData]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.__selected_node = SelectedNodeAddress(self.context)
        self.__nodes_list = NodesList(self.context)
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
        if self._in_nodes_list_mode():  # it is handled by the on_select_changed event
            return

        if not self._is_valid():
            Notification(
                "Invalid node address. Please enter it in a valid format (e.g. https://api.hive.blog)",
                category="error",
            ).show()
            return

        self.app.profile_data.node_address = NodeAddress.parse(self.__get_node_address_input())
        self.app.profile_data.save()
        self.__selected_node.refresh()

    def on_switch_changed(self) -> None:
        self.__nodes_list.toggle_class("-hidden")
        self.__manual_node.toggle_class("-hidden")

    def _is_valid(self) -> bool:
        if self._in_nodes_list_mode():  # Skip validation if the nodes list mode is active
            return True

        try:
            NodeAddress.parse(self.__get_node_address_input())
        except NodeAddressError:
            return False
        else:
            return True

    def _in_nodes_list_mode(self) -> bool:
        """Returns True if the nodes list (combobox) mode is active, False otherwise."""
        return not self.app.query_one(ModeSwitch).value

    def __get_node_address_input(self) -> str:
        return self.app.query_one("#node-address-input", Input).value


class SetNodeAddressForm(SetNodeAddressBase, FormScreen[ProfileData]):
    def __init__(self, owner: Form[ProfileData]) -> None:
        super().__init__(owner=owner)

    def action_next_screen(self) -> None:
        self.__save_node_address()

    def __save_node_address(self) -> None:
        super().action_save_node_address()
        if not self._in_nodes_list_mode() and self._is_valid():
            Notification("Node address saved. Press `CTRL+N` to continue.", category="success").show()
            return

        if self._in_nodes_list_mode():
            self._owner.action_next_screen()
            Notification(f"Node address set to `{self.app.profile_data.node_address}`.", category="success").show()


class SetNodeAddress(SetNodeAddressBase):
    BINDINGS = [Binding("escape", "pop_screen", "Cancel")]

    @property
    def context(self) -> ProfileData:
        return self.app.profile_data
