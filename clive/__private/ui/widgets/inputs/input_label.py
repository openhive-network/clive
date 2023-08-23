from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Label

if TYPE_CHECKING:
    from rich.console import RenderableType


class InputLabel(Label):
    DEFAULT_CSS = """
        InputLabel {
            padding: 1 2;
            text-align: right;
            width: 1fr;
        }
    """

    def __init__(self, renderable: RenderableType = "", id_: str | None = None, classes: str | None = None):
        super().__init__(renderable=f"{renderable.capitalize()}:", id=id_, classes=classes)  # type: ignore
