from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Vertical
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widgets import Static

from clive.__private.ui.widgets.big_title import BigTitle

if TYPE_CHECKING:
    from rich.console import RenderableType
    from textual.app import ComposeResult


class SubTitle(Static):
    pass


class LocationIndicator(Vertical):
    """
    A widget that can be used to display a user's location in the app with a big title and subtitle.

    Attributes:
        DEFAULT_CSS: Default CSS styles for the widget.
        subtitle: The subtitle to display below the big title.
    """

    DEFAULT_CSS = """
    LocationIndicator {
        height: auto;

        SubTitle {
            width: 1fr;
            text-align: center;
        }
    }
    """
    subtitle: RenderableType = reactive("", init=False)  # type: ignore[assignment]

    def __init__(self, big_title: str, subtitle: RenderableType = "") -> None:
        super().__init__()
        self._big_title = big_title
        self.set_reactive(self.__class__.subtitle, subtitle)  # type: ignore[arg-type]

    def compose(self) -> ComposeResult:
        yield BigTitle(self._big_title)
        if self.subtitle:
            yield self._create_subtitle(self.subtitle)

    def _watch_subtitle(self, new_subtitle: RenderableType) -> None:
        try:
            subtitle_widget = self.query_exactly_one(SubTitle)
        except NoMatches:
            self.mount(self._create_subtitle(new_subtitle))
        else:
            subtitle_widget.update(self._create_subtitle_content(new_subtitle))

    @classmethod
    def _create_subtitle(cls, content: RenderableType) -> SubTitle:
        return SubTitle(cls._create_subtitle_content(content))

    @staticmethod
    def _create_subtitle_content(subtitle: RenderableType) -> RenderableType:
        return f"({subtitle})"
