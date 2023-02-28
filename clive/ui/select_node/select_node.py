from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Static

from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.select.select import Select
from clive.ui.widgets.select.select_item import SelectItem

if TYPE_CHECKING:
    from textual.app import ComposeResult


class SelectNode(BaseScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__selected_node = Static("")

    def create_main_panel(self) -> ComposeResult:
        with Container(id="container"):
            yield Static("Please select a node to connect to.")

            yield Select(
                items=[
                    SelectItem(node, str(node)) for idx, node in enumerate(self.app.profile_data.backup_node_addresses)
                ],
                selected=self.app.profile_data.node_address,
                list_mount="#container",
            )
            yield Static()
            yield self.__selected_node

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.selected:
            text = f"Selected node: {event.selected.text}"
            self.__selected_node.update(text)

            self.app.profile_data.node_address = event.selected.value
            self.app.profile_data.save()
