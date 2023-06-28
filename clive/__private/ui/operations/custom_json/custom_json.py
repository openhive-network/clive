from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import CustomJsonOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation


class Body(Grid):
    """All the content of the screen, excluding the title"""


class CustomJson(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__required_auths_input = Input(placeholder="e.g.: alice,bob,charlie")
        self.__required_posting_auths_input = Input(placeholder="e.g: alice,bob,charlie")
        self.__id_input = Input(value="0")
        self.__json_input = Input(placeholder="Custom json data e.g: {}")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Custom json")
            with Body():
                yield Static("required auths", classes="label")
                yield self.__required_auths_input
                yield Static("required posting auths", classes="label")
                yield self.__required_posting_auths_input
                yield Static("id", classes="label")
                yield self.__id_input
                yield Static("json", classes="label")
                yield self.__json_input

    def _create_operation(self) -> Operation | None:
        required_auths_in_list = self.__required_auths_input.value.split(",")
        required_auths_in_list = [x.strip(" ") for x in required_auths_in_list]

        required_posting_auths_in_list = self.__required_posting_auths_input.value.split(",")
        required_posting_auths_in_list = [x.strip(" ") for x in required_posting_auths_in_list]
        return CustomJsonOperation(
            required_auths=required_auths_in_list,
            required_posting_auths=required_posting_auths_in_list,
            id_=int(self.__id_input.value),
            json_=self.__json_input.value,
        )
