from __future__ import annotations

from textual.widgets import TabbedContent


class CliveTabbedContent(TabbedContent):
    DEFAULT_CSS = """
    CliveTabbedContent {
        height: 1fr;  /* needed for proper scroll handling */
    }
    """
