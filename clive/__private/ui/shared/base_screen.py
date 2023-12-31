from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from textual.widgets import Footer

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.widgets.clive_screen import CliveScreen
from clive.__private.ui.widgets.header import Header

if TYPE_CHECKING:
    from textual.app import ComposeResult


class BaseScreen(CliveScreen[None], AbstractClassMessagePump):
    def compose(self) -> ComposeResult:
        yield Header()
        yield from self.create_main_panel()
        yield Footer()

    @abstractmethod
    def create_main_panel(self) -> ComposeResult:
        """Should yield the main panel widgets."""
