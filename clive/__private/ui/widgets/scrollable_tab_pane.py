from __future__ import annotations

from textual.widgets import TabPane


class ScrollableTabPane(TabPane):
    """Tab with auto overflow-y to provide auto-scroll."""

    DEFAULT_CSS = """
    /* padding is added, because textual cut off last element of TabPane*/
    ScrollableTabPane {
        overflow-y: auto;
        padding-bottom: 4;
    }
    """
