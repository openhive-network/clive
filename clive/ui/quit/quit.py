from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Button, Static

from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.dialog_container import DialogContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Quit(BaseScreen):
    BINDINGS = [
        Binding("ctrl+c", "exit_cleanly", "Quit"),
        Binding("escape", "pop_screen", "Cancel"),
    ]

    def on_mount(self) -> None:
        self.query(Button).first().focus()

    def create_main_panel(self) -> ComposeResult:
        yield DialogContainer(
            Static("Are you sure you want to quit?", id="question"),
            Static("(You can also confirm by pressing Ctrl+C again)", id="hint"),
            Horizontal(
                Button("Quit", variant="error", id="quit"),
                Button("Cancel", variant="primary", id="cancel"),
                id="buttons",
            ),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.action_exit_cleanly()
        else:
            self.app.pop_screen()

    def action_exit_cleanly(self) -> None:
        self.log("Exiting cleanly")
        self.app.profile_data.save()
        self.app.exit(0, "CLIVE says goodbye!")
