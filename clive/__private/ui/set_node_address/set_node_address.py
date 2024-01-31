from __future__ import annotations

from abc import ABC
from datetime import datetime
from typing import TYPE_CHECKING, Any, Final

from rich.highlighter import Highlighter
from textual import on
from textual.binding import Binding
from textual.containers import Container, ScrollableContainer
from textual.widgets import Select, Static
from textual.widgets._select import NoSelection

from clive.__private.core.communication import Communication
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.shared.form_screen import FormScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.can_focus_with_scrollbars_only import CanFocusWithScrollbarsOnly
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.core.url import Url
from clive.exceptions import CommunicationError, NodeAddressError
from schemas.jsonrpc import JSONRPCRequest

if TYPE_CHECKING:
    from rich.console import RenderableType
    from rich.text import Text
    from textual.app import ComposeResult

    from clive.__private.core.profile_data import ProfileData
    from clive.__private.ui.shared.form import Form


class ScrollablePart(ScrollableContainer, CanFocusWithScrollbarsOnly):
    """All the content of the screen, excluding the title."""


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


class SetNodeAddressBase(BaseScreen, ABC):
    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.__selected_node = SelectedNodeAddress()
        self.__nodes_list = NodesList()

    def create_main_panel(self) -> ComposeResult:
        yield BigTitle("set node address")
        with ScrollablePart():
            yield self.__selected_node
            yield Static()
            yield self.__nodes_list

    async def _valid_and_save_address(self) -> None:
        address = self.query_one(NodeSelector).value
        assert not isinstance(address, NoSelection), "No node was selected."
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


class SetNodeAddressForm(SetNodeAddressBase, FormScreen[None]):
    def __init__(self, owner: Form[ProfileData]) -> None:
        super().__init__(owner=owner)

    async def apply_and_validate(self) -> None:
        await self._valid_and_save_address()


class SetNodeAddress(SetNodeAddressBase):
    BINDINGS = [Binding("escape", "pop_screen", "Back")]
