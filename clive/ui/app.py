from __future__ import annotations

from pathlib import Path

from textual.app import App
from textual.binding import Binding

from clive.ui.dashboard.dashboard import Dashboard
from clive.ui.quit.quit import Quit
from clive.version import VERSION_INFO


class Clive(App[int]):
    """A singleton instance of the Clive app."""

    SUB_TITLE = VERSION_INFO

    CSS_PATH = [
        Path(__file__).parent / "quit/quit.scss",
    ]

    BINDINGS = [
        Binding("ctrl+c", "push_screen('quit')", "Quit"),
    ]

    SCREENS = {
        "quit": Quit,
        "dashboard": Dashboard,
    }

    def on_mount(self) -> None:
        self.push_screen("dashboard")


clive_app = Clive()
