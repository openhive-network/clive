from __future__ import annotations

from rich.text import Text
from textual.widgets import Static


class EllipsedStatic(Static):
    """A static widget that renders a string with ellipsis if it overflows."""

    def __init__(self, renderable: str = "", *, id_: str | None = None, classes: str | None = None) -> None:
        super().__init__(id=id_, classes=classes)
        self.__renderable = renderable

    def render(self) -> Text:
        return Text(self.__renderable, no_wrap=True, overflow="ellipsis")
