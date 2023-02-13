from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Placeholder

from clive.ui.shared.base_screen import BaseScreen

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Dashboard(BaseScreen):
    def create_main_panel(self) -> ComposeResult:
        yield Placeholder("Dashboard content goes here")
