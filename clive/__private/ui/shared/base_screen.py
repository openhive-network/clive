from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, ClassVar

from textual.reactive import Reactive, reactive
from textual.widgets import Footer

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.widgets.clive_screen import CliveScreen
from clive.__private.ui.widgets.header import Header
from clive.__private.ui.widgets.location_indicator import LocationIndicator

if TYPE_CHECKING:
    from textual.app import ComposeResult


class BaseScreen(CliveScreen[None], AbstractClassMessagePump):
    BIG_TITLE: ClassVar[str] = ""
    SUBTITLE: ClassVar[str] = ""
    subtitle: Reactive[str] = reactive("")

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self.subtitle = self.SUBTITLE

    def compose(self) -> ComposeResult:
        yield Header()
        if self.BIG_TITLE:
            yield LocationIndicator(self.BIG_TITLE, self.subtitle)
        yield from self.create_main_panel()
        yield Footer()

    @abstractmethod
    def create_main_panel(self) -> ComposeResult:
        """Should yield the main panel widgets."""
