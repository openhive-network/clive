from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Static

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.buttons import CliveButton
from clive.__private.ui.widgets.dialog_container import DialogContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Quit(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [
        Binding("ctrl+x", "exit_cleanly", "Quit"),
        Binding("escape", "cancel", "Back"),
    ]

    SHOW_RAW_HEADER = True

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer():
            yield Static("Are you sure you want to quit?", id="question")
            yield Static("(You can also confirm by pressing Ctrl+X again)", id="hint")
            with Horizontal(id="buttons"):
                yield CliveButton("Quit", variant="error", id_="quit")
                yield CliveButton("Cancel", id_="cancel")

    @on(CliveButton.Pressed, "#cancel")
    def action_cancel(self) -> None:
        self.app.pop_screen()

    @on(CliveButton.Pressed, "#quit")
    def action_exit_cleanly(self) -> None:
        # Profile saving is done when exiting World contextmanager
        self.log("Exiting cleanly")
        self.app.exit(message="CLIVE says goodbye!")
