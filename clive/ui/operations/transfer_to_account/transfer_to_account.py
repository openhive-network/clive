from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Grid, Horizontal
from textual.widgets import Button, Input, Static

from clive.models.transfer_operation import TransferOperation
from clive.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.ui.widgets.big_title import BigTitle
from clive.ui.widgets.ellipsed_static import EllipsedStatic
from clive.ui.widgets.select.select import Select
from clive.ui.widgets.select.select_item import SelectItem
from clive.ui.widgets.view_bag import ViewBag

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class Buttons(Horizontal):
    """Container for the buttons"""


class CurrencySelector(Select):
    def __init__(self) -> None:
        super().__init__(
            items=[SelectItem(0, "HIVE"), SelectItem(1, "HBD")],
            list_mount="ViewBag",
            placeholder="Select currency",
        )


class TransferToAccount(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Operations"),
        Binding("f1", "finalize", "Finalize"),
        Binding("f2", "add_to_cart", "Add to cart"),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__to_input = Input(placeholder="e.g.: some-account")
        self.__amount_input = Input(placeholder="e.g.: 5.000")
        self.__memo_input = Input(placeholder="e.g.: For the coffee!")
        self.__currency_selector = CurrencySelector()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Transfer to account")
            with Body():
                yield Static("from", classes="label")
                yield EllipsedStatic(str(self.app.profile_data.active_account.name), id_="from-label")
                yield PlaceTaker()
                yield Static("to", classes="label")
                yield self.__to_input
                yield Static("amount", classes="label")
                yield self.__amount_input
                yield self.__currency_selector
                yield Static("memo", classes="label")
                yield self.__memo_input
                yield Static()
                yield Static()
                with Buttons():
                    yield Button("Finalize transaction", id="finalize-button")
                    yield Button("Add to cart", id="add-to-cart-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "finalize-button":
            self.action_finalize()
        elif event.button.id == "add-to-cart-button":
            self.action_add_to_cart()

    def action_finalize(self) -> None:
        self.__collect_data()

    def action_add_to_cart(self) -> None:
        self.__collect_data()

    def __collect_data(self) -> None:
        op = TransferOperation(
            asset=self.__currency_selector.text,
            from_=str(self.app.profile_data.active_account.name),
            to=self.__to_input.value,
            amount=self.__amount_input.value,
            memo=self.__memo_input.value,
        )
        if op.is_valid():
            self.app.profile_data.operations_cart.append(op)
            self.app.update_reactive("profile_data")
