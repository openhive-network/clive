from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widget import Widget
from textual.widgets import Label

if TYPE_CHECKING:
    from rich.console import RenderableType
    from textual.app import ComposeResult


class TitledLabel(Widget):
    def __init__(self, title: RenderableType, value: RenderableType) -> None:
        super().__init__()
        self.title = title
        self.value = value

    def compose(self) -> ComposeResult:
        yield Label(f"{self.title}:", id="title")
        yield Label(f" {self.value}", id="value")
