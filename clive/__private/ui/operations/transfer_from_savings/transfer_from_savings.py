from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.currency_selector_liquid import CurrencySelectorLiquid
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import TransferFromSavingsOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class TransferFromSavings(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__request_id_input = Input(placeholder="e.g.: 1000, notice: default value is 0")
        self.__amount_input = Input(placeholder="e.g.: 5.000")
        self.__memo_input = Input(placeholder="e.g.: For the coffee!")
        self.__currency_selector = CurrencySelectorLiquid()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Transfer from savings")
            with Body():
                yield Static("from", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="from-label")
                yield PlaceTaker()
                yield Static("request id", classes="label")
                yield self.__request_id_input
                yield Static("amount", classes="label")
                yield self.__amount_input
                yield self.__currency_selector
                yield Static("memo", classes="label")
                yield self.__memo_input

    def _create_operation(self) -> Operation | None:
        return TransferFromSavingsOperation(
            from_=str(self.app.world.profile_data.working_account.name),
            request_id=int(self.__request_id_input.value),
            amount=self.__currency_selector.selected.value(float(self.__amount_input.value)),
            memo=self.__memo_input.value,
        )
