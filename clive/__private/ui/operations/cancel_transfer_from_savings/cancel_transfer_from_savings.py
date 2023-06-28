from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
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

        self.__request_id_input = Input(placeholder="e.g.: 1000. Notice: default value is 0")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Cancel transfer from savings")
            with Body():
                yield Static("from", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="from-label")
                yield PlaceTaker()
                yield Static("request_id", classes="label")
                yield self.__request_id_input

    def _create_operation(self) -> Operation | None:
        return CancelTransferFromSavingsOperation(
            From=str(self.app.world.profile_data.working_account.name),
            request_id=int(self.__request_id_input.value),
        )
