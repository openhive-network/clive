from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Button, Static

from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.big_title import BigTitle
from clive.ui.widgets.select.select import Select
from clive.ui.widgets.select.select_item import SelectItem
from clive.ui.widgets.view_bag import ViewBag

if TYPE_CHECKING:
    from textual.app import ComposeResult


class TransactionSummary(BaseScreen):
    BINDINGS = [
        Binding("escape", "to_dashboard", "Escape"),
        Binding("f10", "save", "Save"),
        Binding("f11", "broadcast", "Broadcast"),
    ]

    def create_main_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("transaction")
            with Container(id="trx_summary_operations_container"):
                yield Static("This transaction will contain following operations in presented order")
                for op in self.app.profile_data.operations_cart:
                    yield Static(str(op))

            with Horizontal():
                yield Static("Sign with authority:")
                yield Select(
                    [SelectItem(x, x.key_name) for x in self.app.profile_data.active_account.keys], list_mount="ViewBag"
                )

            yield Button("🔥 clear all")
            yield Button("💾 save")
            yield Button("🌐 broadcast")

    def action_save(self) -> None:
        selected = self.query_one("Select", expect_type=Select).selected
        with Path("trx.json").open("wt") as file:
            json.dump(
                {
                    "ops_in_trx": self.app.profile_data.operations_cart,
                    "selected_authority": str(selected.value if selected is not None else ""),
                },
                file,
                default=vars,
            )

    def __clear_all(self) -> None:
        self.app.profile_data.operations_cart.clear()
        self.app.get_widget_by_id("trx_summary_operations_container").add_class("deleted")

    def action_broadcast(self) -> None:
        self.__clear_all()
        self.action_to_dashboard()

    def action_to_dashboard(self) -> None:
        while len(self.app.screen_stack) != 0:
            self.app.pop_screen()
