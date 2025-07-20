from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Vertical
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
        DEFAULT_CSS: The default CSS styles for the widget.

    Args:
        big_title: The main title to display prominently.
        subtitle: An optional subtitle to provide additional context.
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

    def __init__(self, big_title: str, subtitle: RenderableType = "") -> None:
        super().__init__()
        self._big_title = big_title
        self._subtitle = subtitle

    def compose(self) -> ComposeResult:
        yield BigTitle(self._big_title)
        if self._subtitle:
            yield SubTitle(f"({self._subtitle})")
