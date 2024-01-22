from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import TabPane

from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from rich.text import TextType


class PowerDown(TabPane, CliveWidget):
    """TabPane with all content about power down."""

    def __init__(self, title: TextType):
        """
        Initialize a TabPane.

        Args:
        ----
        title: Title of the TabPane (will be displayed in a tab label).
        """
        super().__init__(title=title)
