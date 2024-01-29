from __future__ import annotations

from textual.widgets import Label


class Notice(Label):
    DEFAULT_CSS = """
    Notice {
        color: $text;
        background: $warning;
        text-align: center;
        height: 1;
        width: 1fr;
    }
    """

    def __init__(self, text: str) -> None:
        super().__init__(f"[bold]Notice:[/bold] {text}")
