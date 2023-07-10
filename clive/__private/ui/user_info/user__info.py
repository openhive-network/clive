from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Static

from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.view_bag import ViewBag

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Static, can_focus=True):
    """wip"""


class UserInfo(BaseScreen):
    def create_main_panel(self) -> ComposeResult:
        with ViewBag(), Body():
            yield Static("wip")
