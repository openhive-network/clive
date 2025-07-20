from __future__ import annotations

from textual.widgets import Static


class PlaceTaker(Static):
    """
    A widget that takes up space but does not render anything.

    Attributes:
        DEFAULT_CSS: The default CSS styles for the widget.
    """

    DEFAULT_CSS = """
    PlaceTaker {
        min-height: 1;
    }
    """
