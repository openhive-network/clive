from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.widgets import Static

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.set_node_address.set_node_address import SetNodeAddress
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.dialog_container import DialogContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ConfigBase(BaseScreen, AbstractClassMessagePump):
    CSS_PATH = [get_relative_css_path(__file__, name="config")]

    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
    ]

    def additional_buttons(self) -> ComposeResult:
        """Returns the additional buttons to be displayed on the configuration screen."""
        return []

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer():
            yield Static("Please choose which configuration you would like to make:", id="hint")
            yield CliveButton("Select node", id_="select-node")
            yield from self.additional_buttons()

    @on(CliveButton.Pressed, "#select-node")
    def push_set_node_address_screen(self) -> None:
        self.app.push_screen(SetNodeAddress())
