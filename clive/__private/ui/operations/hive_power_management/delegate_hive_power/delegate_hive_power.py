from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Static

from clive.__private.ui.operations.hive_power_management.common_hive_power.hp_tab_pane import HPTabPane

if TYPE_CHECKING:
    from textual.app import ComposeResult


class DelegateHivePower(HPTabPane):
    """TabPane with all content about delegate hp."""

    def create_tab_pane_content(self) -> ComposeResult:
        """Will be implemented in next MR."""
        yield Static("In progress")
