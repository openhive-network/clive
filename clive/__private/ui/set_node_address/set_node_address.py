from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any, Final

from rich.highlighter import Highlighter
from textual import on
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Select, Static
from textual.widgets._select import NoSelection

from clive.__private.core.communication import Communication
from clive.__private.core.date_utils import utc_now
from clive.__private.core.url import Url
from clive.__private.models.schemas import JSONRPCRequest
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.screens.form_screen import FormScreen
from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.clive_basic.clive_widget import CliveWidget
from clive.__private.ui.widgets.section import SectionScrollable
from clive.exceptions import CommunicationError, NodeAddressError

if TYPE_CHECKING:
    from rich.console import RenderableType
    from rich.text import Text
    from textual.app import ComposeResult

    from clive.__private.core.profile import Profile
    from clive.__private.ui.shared.form import Form


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


class NodeUrlHighlighter(Highlighter):
    def __init__(self) -> None:
        self.__last_highlight_time = utc_now()
        self.__last_style = "white"
        super().__init__()

    def __check_and_update_highlight_period(self) -> bool:
        highlight_period: Final[int] = 1
        now = utc_now()
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
        # Section is focusable bcs it's not possible to use scrolling via keyboard when Select is focused
        with SectionScrollable("Set node address", focusable=True):
            yield self.__selected_node
            yield self.__nodes_list

    async def _valid_and_save_address(self) -> None:
        address = self.query_one(NodeSelector).value
        assert not isinstance(address, NoSelection), "No node was selected."
        await self.node.set_address(address)
        self.app.trigger_node_watchers()
        self.__selected_node.refresh()

    @on(NodeSelector.Changed)
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
            self.notify(f"Node address set to `{self.node.address}`.")


class SetNodeAddressForm(SetNodeAddressBase, FormScreen[None]):
    BIG_TITLE = "onboarding"

    def __init__(self, owner: Form[Profile]) -> None:
        super().__init__(owner=owner)

    async def apply_and_validate(self) -> None:
        await self._valid_and_save_address()


class SetNodeAddress(SetNodeAddressBase):
    BIG_TITLE = "configuration"
    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]
