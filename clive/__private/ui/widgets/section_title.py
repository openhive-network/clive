from __future__ import annotations

from textual.widgets import Static


class SectionTitle(Static):
    DEFAULT_CSS = """
    SectionTitle {
        text-style: bold;
        background: $primary;
        width: 1fr;
        height: 1;
        text-align: center;
    }
    """

    def __init__(self, title: str, id_: str | None = None, classes: str | None = None) -> None:
        super().__init__(renderable=title, id=id_, classes=classes)
