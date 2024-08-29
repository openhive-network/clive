from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

from textual.reactive import reactive
from textual.widgets import Footer

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.clive_screen import CliveScreen
from clive.__private.ui.widgets.clive_basic import CliveHeader
from clive.__private.ui.widgets.location_indicator import LocationIndicator

if TYPE_CHECKING:
    from textual.app import ComposeResult


class BaseScreen(CliveScreen[None], AbstractClassMessagePump):
    BIG_TITLE: ClassVar[str] = ""
    SUBTITLE: ClassVar[str] = ""
    """Subtitle won't be shown when BIG_TITLE is not set also"""
    subtitle: str = reactive("", recompose=True)  # type: ignore[assignment]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.subtitle = self.SUBTITLE

    def compose(self) -> ComposeResult:
        yield CliveHeader()
        if self.BIG_TITLE:
            yield LocationIndicator(self.BIG_TITLE, self.subtitle)
        yield from self.create_main_panel()
        yield Footer()

    @abstractmethod
    def create_main_panel(self) -> ComposeResult:
        """Yield the main panel widgets."""
