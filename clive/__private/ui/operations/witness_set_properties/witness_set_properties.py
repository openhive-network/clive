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
from clive.models import Asset, Operation
from schemas.operations import WitnessSetPropertiesOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class WitnessSetProperties(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__witness_input = Input(placeholder="e.g: hiveio")
        self.__account_creation_fee_input = Input(placeholder="account creation fee, e.g: 1.000")
        self.__maximum_block_size_input = Input(value="131072", placeholder="maximum block size")
        self.__hbd_interest_rate_input = Input(value="1000", placeholder="hbd interest rate")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Witness set properties")
            with Body():
                yield Static("witness", classes="label")
                yield self.__witness_input
                yield BigTitle("Props")
                yield PlaceTaker()
                yield Static("account creation fee", classes="label")
                yield self.__account_creation_fee_input
                yield Static("maximum block size", classes="label")
                yield self.__maximum_block_size_input
                yield Static("hbd interest rate", classes="label")
                yield self.__hbd_interest_rate_input

    def create_operation(self) -> Operation | None:
        try:
            props_field = {
                "account_creation_fee": Asset.hive(float(self.__account_creation_fee_input.value)),
                "maximum_block_size": int(self.__maximum_block_size_input.value),
                "hbd_interest_rate": int(self.__hbd_interest_rate_input.value),
            }

            return WitnessSetPropertiesOperation(witness=self.__witness_input.value, props=props_field)  # noqa: TRY300
        except ValidationError as error:
            Notification(f"Operation failed the validation process.\n{error}", category="error").show()
            return None
