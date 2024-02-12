from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from textual.widgets import TabPane

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.operations.hive_power_management.common_hive_power.hp_information_table import (
    HpInformationTable,
)
from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult


class HPTabPane(TabPane, CliveWidget, AbstractClassMessagePump):
    """TabPane created to catch when is activated and mount `hp_information_table` at this moment."""

    def __init__(self, title: TextType):
        """
        Initialize a TabPane.

        Args:
        ----
        title: Title of the TabPane (will be displayed in a tab label).
        """
        super().__init__(title=title)

    def compose(self) -> ComposeResult:
        yield from self.create_header()
        yield HpInformationTable()
        yield from self.create_tab_pane_content()

    @abstractmethod
    def create_tab_pane_content(self) -> ComposeResult:
        """Method used to create all contents of TabPane except hp_information_table - managed in TabbedContent."""

    def create_header(self) -> ComposeResult:
        """Must be overridden if you want to create a header for TapPane."""
        return []
