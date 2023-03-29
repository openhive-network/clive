from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from textual.binding import Binding
from textual.widgets import Button, Static

from clive.abstract_class import AbstractClassMessagePump
from clive.ui.set_node_address.set_node_address import SetNodeAddress
from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.clive_button import CliveButton
from clive.ui.widgets.dialog_container import DialogContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ConfigBase(BaseScreen, AbstractClassMessagePump):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
    ]

    def additional_buttons(self) -> Iterable[Button]:
        """Returns the additional buttons to be displayed on the configuration screen."""
        return []

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer():
            yield Static("Please choose which configuration you would like to make:", id="hint")
            yield CliveButton("Select node", id_="select-node")
            yield from self.additional_buttons()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "select-node":
            self.app.push_screen(SetNodeAddress())
