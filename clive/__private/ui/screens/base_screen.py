from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

from textual import on
from textual.reactive import reactive
from textual.widgets import Footer

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.clive_screen import CliveScreen, ScreenResultT
from clive.__private.ui.widgets.clive_basic import CliveHeader, CliveRawHeader
from clive.__private.ui.widgets.clive_basic.clive_header import NodeStatus
from clive.__private.ui.widgets.location_indicator import LocationIndicator

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.node import Node


class BaseScreen(CliveScreen[ScreenResultT], AbstractClassMessagePump):
    BIG_TITLE: ClassVar[str] = ""
    SUBTITLE: ClassVar[str] = ""
    """Subtitle won't be shown when BIG_TITLE is not set also"""
    SHOW_RAW_HEADER: ClassVar[bool] = False
    subtitle: str = reactive("", recompose=True)  # type: ignore[assignment]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.subtitle = self.SUBTITLE

    def compose(self) -> ComposeResult:
        yield CliveHeader() if not self.SHOW_RAW_HEADER else CliveRawHeader()
        if self.BIG_TITLE:
            yield LocationIndicator(self.BIG_TITLE, self.subtitle)
        yield from self.create_main_panel()
        yield Footer()

    @on(NodeStatus.ChangeNodeAddress)
    def push_switch_node_address_dialog(self) -> None:
        from clive.__private.ui.dialogs.switch_node_address_dialog import SwitchNodeAddressDialog

        self.app.push_screen(SwitchNodeAddressDialog(self.get_node()))

    @abstractmethod
    def create_main_panel(self) -> ComposeResult:
        """Yield the main panel widgets."""

    def get_node(self) -> Node:
        """Override this method to return the node other than the one in the world."""
        return self.world.node
