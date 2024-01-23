from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import TabPane

from clive.__private.ui.operations.hive_power_management.common_hive_power.hp_information_table import (
    HpInformationTable,
)
from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult


class DelegateHivePower(TabPane, CliveWidget):
    """TabPane with all content about delegate hp."""

    def __init__(self, title: TextType):
        """
        Initialize a TabPane.

        Args:
        ----
        title: Title of the TabPane (will be displayed in a tab label).
        """
        super().__init__(title=title)

    def compose(self) -> ComposeResult:
        yield HpInformationTable()
