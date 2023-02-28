from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from textual.widgets import Footer

from clive.abstract_class import AbstractClassMessagePump
from clive.ui.terminal.terminal import Terminal
from clive.ui.widgets.clive_screen import CliveScreen
from clive.ui.widgets.header import Header

if TYPE_CHECKING:
    from textual.app import ComposeResult


class BaseScreen(CliveScreen, AbstractClassMessagePump):
    def compose(self) -> ComposeResult:
        yield Header()
        yield from self._create_main_panel()
        yield Terminal()
        yield Footer()

    def _create_main_panel(self) -> ComposeResult:
        """Proxy method to be override by other implementations of Clive Screen"""
        yield from self.create_main_panel()

    @abstractmethod
    def create_main_panel(self) -> ComposeResult:
        """Should yield the main panel widgets."""
