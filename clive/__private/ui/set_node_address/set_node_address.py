from __future__ import annotations

from abc import ABC
from datetime import datetime
from typing import TYPE_CHECKING, Any, Final

from rich.highlighter import Highlighter
from textual import on
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.widgets import Input, Select, Static, Switch

from clive.__private.core.communication import Communication
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.shared.form_screen import FormScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.core.url import Url
from clive.exceptions import CommunicationError, NodeAddressError
from schemas.jsonrpc import JSONRPCRequest

if TYPE_CHECKING:
    from rich.console import RenderableType
    from rich.text import Text
    from textual.app import ComposeResult

    from clive.__private.core.profile_data import ProfileData
    from clive.__private.ui.shared.form import Form


class ScrollablePart(ScrollableContainer):
    """All the content of the screen, excluding the title."""


class ModeSwitch(Switch):
    """A switch that changes the way the node address is selected."""


class NodeSelector(Select[Url], CliveWidget):
    """Select for the node address."""

    def __init__(self) -> None:
        super().__init__(
            [(str(url), url) for url in self.app.world.profile_data.backup_node_addresses],
            allow_blank=False,
            value=self.app.world.node.address,
        )


class SelectedNodeAddress(Static, CliveWidget):
    """The currently selected node address."""

    def render(self) -> RenderableType:
        return f"Selected node address: {self.app.world.node.address}"


class NodesList(Container, CliveWidget):
    def compose(self) -> ComposeResult:
        yield Static("Please select the node you want to connect to from the predefined list below.")
        yield NodeSelector()


class NodeUrlHighlighter(Highlighter):
    def __init__(self) -> None:
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
        try:
            Communication().request(url, data=JSONRPCRequest(method="database_api.get_config"))
        except CommunicationError:
            return False
        return True

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
            placeholder=f"e.g.: {self.app.world.node.address}",
            id="node-address-input",
            highlighter=NodeUrlHighlighter(),
        )
        yield CliveButton("Save", id_="save-node-address-button")


class ModeSwitchContainer(Horizontal):
    def compose(self) -> ComposeResult:
        yield ModeSwitch()
        yield Static("Toggle mode")


class SetNodeAddressBase(BaseScreen, ABC):
    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.__selected_node = SelectedNodeAddress()
        self.__nodes_list = NodesList()
        self.__manual_node = ManualNode(classes="-hidden")

    def create_main_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("set node address")
            with ScrollablePart():
                yield self.__selected_node
                yield Static()
                yield ModeSwitchContainer(disabled=True)
                yield Static()
                yield self.__nodes_list
                yield self.__manual_node

    async def _valid_and_save_address(self) -> None:
        if self._in_nodes_list_mode():
            address = self.query_one(Select).value
            assert address is not None
        else:
            address = Url.parse(self.app.query_one("#node-address-input", Input).value)
        await self.app.world.node.set_address(address)
        self.app.trigger_node_watchers()
        self.__selected_node.refresh()

    @on(Select.Changed)
    @on(CliveButton.Pressed, "#save-node-address-button")
    async def save_node_address_with_gui_support(self) -> None:
        try:
            await self._valid_and_save_address()
        except NodeAddressError:
            self.notify(
                "Invalid node address. Please enter it in a valid format (e.g. https://api.hive.blog)",
                severity="error",
            )
        else:
            self.notify(f"Node address set to `{self.app.world.node.address}`.")

    @on(Switch.Changed)
    def change_mode(self) -> None:
        self.__nodes_list.toggle_class("-hidden")
        self.__manual_node.toggle_class("-hidden")

    def _in_nodes_list_mode(self) -> bool:
        """Returns True if the nodes list (combobox) mode is active, False otherwise."""
        return not self.app.query_one(ModeSwitch).value


class SetNodeAddressForm(SetNodeAddressBase, FormScreen[None]):
    def __init__(self, owner: Form[ProfileData]) -> None:
        super().__init__(owner=owner)

    async def apply_and_validate(self) -> None:
        await self._valid_and_save_address()


class SetNodeAddress(SetNodeAddressBase):
    BINDINGS = [Binding("escape", "pop_screen", "Back")]
