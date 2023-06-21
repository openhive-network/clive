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
from schemas.operations import CancelTransferFromSavingsOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class CancelTransferFromSavings(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__from_input = Input(placeholder="e.g.: alice")
        self.__request_id_input = Input(placeholder="e.g.: 1000. Notice: default value is 0")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Cancel transfer from savings")
            with Body():
                yield Static("from", classes="label")
                yield self.__from_input
                yield Static("request_id", classes="label")
                yield self.__request_id_input

    def create_operation(self) -> Operation | None:
        try:
            if self.__request_id_input.value:
                return CancelTransferFromSavingsOperation(
                    From=self.__from_input.value, request_id=self.__request_id_input.value
                )
            return CancelTransferFromSavingsOperation(From=int(self.__from_input.value))  # noqa: TRY300

        except ValidationError as error:
            Notification(f"Operation failed the validation process.\n{error}", category="error").show()
            return None
