from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header

from clive.version import VERSION_INFO


class Clive(App[int]):
    """A singleton instance of the Clive app."""

    SUB_TITLE = VERSION_INFO

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()

    async def action_quit(self) -> None:
        self.log.debug("ctrl+c pressed, quitting...")
        self.exit(0, "CLIVE says goodbye!")


clive_app = Clive()
