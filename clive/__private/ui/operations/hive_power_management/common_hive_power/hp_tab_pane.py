from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from textual.containers import Container
from textual.widgets import Static, TabPane

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.operations.hive_power_management.common_hive_power.hp_information_table import (
    HpInformationTable,
)
from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult


class ContainerForInformationTable(Container):
    """Container used to mount hp information table inside."""

    DEFAULT_CSS = """
    ContainerForInformationTable {
        height: auto;
    }

    Static {
        text-align: center;
        text-style: bold;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("Loading...")

    async def set_loaded(self) -> None:
        await self.query("*").remove()


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
        self._container_for_table = ContainerForInformationTable()
        self._is_table_mounted = False

    def compose(self) -> ComposeResult:
        yield from self.create_header()
        yield self._container_for_table
        yield from self.create_tab_pane_content()

    async def mount_hp_table(self) -> None:
        """Method that mount hp_information_table if used for the first time, otherwise - does nothing."""
        if not self._is_table_mounted:
            with self.app.batch_update():
                self._is_table_mounted = True
                await self._container_for_table.set_loaded()
                await self._container_for_table.mount(HpInformationTable())

    @abstractmethod
    def create_tab_pane_content(self) -> ComposeResult:
        """Method used to create all contents of TabPane except hp_information_table - managed in TabbedContent."""

    def create_header(self) -> ComposeResult:
        """Must be overridden if you want to create a header for TapPane."""
        return []
