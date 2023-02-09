from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


class Clive(App[str]):
    """A singleton instance of the Clive app."""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()


clive = Clive()
