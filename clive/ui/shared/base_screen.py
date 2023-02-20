from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from textual.message_pump import MessagePumpMeta
from textual.widgets import Footer

from clive.ui.widgets.clive_screen import CliveScreen
from clive.ui.widgets.header import Header

if TYPE_CHECKING:
    from textual.app import ComposeResult


class MessagePumpABCMeta(MessagePumpMeta, ABCMeta):
    """
    Combine MessagePumpMeta and ABCMeta into a single metaclass.
    Resolves the issue with:
        TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the
        metaclasses of all its bases
    """


class BaseScreen(CliveScreen, metaclass=MessagePumpABCMeta):
    def compose(self) -> ComposeResult:
        yield Header()
        yield from self.create_main_panel()
        yield Footer()

    @abstractmethod
    def create_main_panel(self) -> ComposeResult:
        """Should yield the main panel widgets."""
