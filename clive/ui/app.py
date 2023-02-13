from __future__ import annotations

from textual.app import App
from textual.binding import Binding

from clive.ui.dashboard.dashboard import Dashboard
from clive.version import VERSION_INFO


class Clive(App[int]):
    """A singleton instance of the Clive app."""

    SUB_TITLE = VERSION_INFO

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
    ]

    SCREENS = {
        "dashboard": Dashboard,
    }

    def on_mount(self) -> None:
        self.push_screen("dashboard")

    async def action_quit(self) -> None:
        self.log.debug("ctrl+c pressed, quitting...")
        self.exit(0, "CLIVE says goodbye!")


clive_app = Clive()
