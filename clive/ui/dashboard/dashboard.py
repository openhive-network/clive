from __future__ import annotations

from typing import TYPE_CHECKING

from textual.screen import Screen
from textual.widgets import Footer, Header, Placeholder

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Dashboard(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Placeholder("Dashboard content goes here")
        yield Footer()
