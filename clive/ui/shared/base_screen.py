from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from textual.message_pump import MessagePumpMeta
from textual.screen import Screen
from textual.widgets import Footer

from clive.ui.widgets.header import Header

if TYPE_CHECKING:
    from textual.app import ComposeResult


class MessagePumpMetaABC(MessagePumpMeta, ABCMeta):
    """
    Combine MessagePumpMeta and ABCMeta into a single metaclass.
    Resolves the issue with:
        TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the
        metaclasses of all its bases
    """


class BaseScreen(Screen, metaclass=MessagePumpMetaABC):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield from self.create_main_panel()
        yield Footer()

    @abstractmethod
    def create_main_panel(self) -> ComposeResult:
        """Should yield the main panel widgets."""
