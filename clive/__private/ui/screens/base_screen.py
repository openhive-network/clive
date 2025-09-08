from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

from textual.css.query import NoMatches
from textual.reactive import reactive

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.clive_screen import CliveScreen, ScreenResultT
from clive.__private.ui.widgets.clive_basic import CliveHeader, CliveRawHeader
from clive.__private.ui.widgets.clive_basic.clive_footer import CliveFooter
from clive.__private.ui.widgets.location_indicator import LocationIndicator

if TYPE_CHECKING:
    from rich.console import RenderableType
    from textual.app import ComposeResult


class BaseScreen(CliveScreen[ScreenResultT], AbstractClassMessagePump):
    BIG_TITLE: ClassVar[str] = ""
    SUBTITLE: ClassVar[str] = ""
    """Subtitle won't be shown when BIG_TITLE is not set also"""
    SHOW_RAW_HEADER: ClassVar[bool] = False
    subtitle: RenderableType = reactive("", init=False)  # type: ignore[assignment]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.set_reactive(self.__class__.subtitle, self.SUBTITLE)  # type: ignore[arg-type]

    def compose(self) -> ComposeResult:
        yield CliveHeader() if not self.SHOW_RAW_HEADER else CliveRawHeader()
        if self.BIG_TITLE:
            yield LocationIndicator(self.BIG_TITLE, self.subtitle)
        yield from self.create_main_panel()
        yield CliveFooter()

    @abstractmethod
    def create_main_panel(self) -> ComposeResult:
        """
        Yield the main panel widgets.

        Returns:
            The widgets to be displayed in the main panel.
        """

    def _watch_subtitle(self, new_subtitle: RenderableType) -> None:
        try:
            location_indicator = self.query_exactly_one(LocationIndicator)
        except NoMatches as error:
            raise AssertionError("You can't update subtitle while screen has no big title.") from error
        location_indicator.subtitle = new_subtitle
