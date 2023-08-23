from __future__ import annotations

from textual.widgets import Label


class InputLabel(Label):
    DEFAULT_CSS = """
        InputLabel {
            padding: 1 2;
            text-align: right;
            width: 1fr;
        }
    """

    def __init__(self, renderable: str, id_: str | None = None, classes: str | None = None) -> None:
        super().__init__(renderable=f"{renderable.capitalize()}:", id=id_, classes=classes)
