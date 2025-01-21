from __future__ import annotations

from textual.widgets import Static


class NoContentAvailable(Static):
    DEFAULT_CSS = """
    NoContentAvailable {
        text-style: bold;
        background: $secondary-lighten-1;
        width: 1fr;
        height: 1;
        text-align: center;
    }
    """
