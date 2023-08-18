from __future__ import annotations

from textual.widgets import TabPane


class ScrollableTabPane(TabPane):
    """Tab with auto overflow-y to provide auto-scroll."""

    DEFAULT_CSS = """
    ScrollableTabPane {
        overflow-y: auto;
    }
    """
