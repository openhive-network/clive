from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Quit(Screen):
    BINDINGS = [
        Binding("ctrl+c", "exit_cleanly", "Quit"),
        Binding("escape", "pop_screen", "Cancel"),
    ]

    def on_mount(self) -> None:
        self.query(Button).first().focus()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static("Are you sure you want to quit?", id="question"),
            Static("(You can also confirm by pressing Ctrl+C again)", id="hint"),
            Horizontal(
                Button("Quit", variant="error", id="quit"),
                Button("Cancel", variant="primary", id="cancel"),
                id="buttons",
            ),
            id="dialog",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.action_exit_cleanly()
        else:
            self.app.pop_screen()

    def action_exit_cleanly(self) -> None:
        self.log("Exiting cleanly")
        self.app.exit(0, "CLIVE says goodbye!")
