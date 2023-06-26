from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ValidationError
from textual.binding import Binding
from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.notification import Notification
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import CustomOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation


class Body(Grid):
    """All the content of the screen, excluding the title"""


class Custom(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__required_auths_input = Input(placeholder="e.g.: alice,bob,charlie")
        self.__id_input = Input(value="0")
        self.__data_input = Input(placeholder="Custom data input")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Custom")
            with Body():
                yield Static("required auths", classes="label")
                yield self.__required_auths_input
                yield Static("id", classes="label")
                yield self.__id_input
                yield Static("data", classes="label")
                yield self.__data_input

    def create_operation(self) -> Operation | None:
        try:
            required_auths_in_list = self.__required_auths_input.value.split(",")
            required_auths_in_list = [x.strip(" ") for x in required_auths_in_list]

            return CustomOperation(  # noqa: TRY300
                required_auths=required_auths_in_list,
                id_=int(self.__id_input.value),
                data=[self.__data_input.value],
            )
        except ValidationError as error:
            Notification(f"Operation failed the validation process.\n{error}", category="error").show()
            return None
