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
from clive.models import Asset, Operation
from schemas.operations import LimitOrderCreate2Operation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class ExchangeRatePlaceTaker(Static):
    """Container used for making correct layout of Exchange rate big title"""


class BaseQuotePlaceTaker(Static):
    """Container used for making correct layout of base and quote fields"""


class AmountToSellPlaceTaker(Static):
    """Container used for making correct layout of amount to sell field"""


class LimitOrderCreate2(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__order_id_input = Input(placeholder="e.g.: 1000.", value="0")
        self.__fill_or_kill_input = Input(placeholder="e.g.: True.", value="False")
        self.__expiration_input = Input(placeholder="e.g.: 2023-01-01T00:00:00")
        self.__amount_to_sell_input = Input(placeholder="e.g.: 1.000")
        self.__base_input = Input(placeholder="e.g: 1")
        self.__quote_input = Input(placeholder="e.g: 10")
        self.__currency_selector_amount_to_sell = CurrencySelectorLiquid()
        self.__currency_selector_base = CurrencySelectorLiquid()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Limit order create2")
            with Body():
                yield Static("owner", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="owner-label")
                yield PlaceTaker()
                yield Static("order id", classes="label")
                yield self.__order_id_input
                yield Static("fill or kill", classes="label")
                yield self.__fill_or_kill_input
                yield Static("expiration", classes="label")
                yield self.__expiration_input
                yield AmountToSellPlaceTaker()
                yield Static("amount to sell", classes="label")
                yield self.__amount_to_sell_input
                yield self.__currency_selector_amount_to_sell
                yield ExchangeRatePlaceTaker()
                yield BigTitle("Exchange rate")
                yield BaseQuotePlaceTaker()
                yield Static("base", classes="label")
                yield self.__base_input
                yield self.__currency_selector_base
                yield Static("quote", classes="label")
                yield self.__quote_input

    def _create_operation(self) -> Operation | None:
        exchange_rate = {
            "base": self.__currency_selector_base.selected.value(float(self.__base_input.value)),
            "quote": Asset.hive(float(self.__quote_input.value)),
        }

        return LimitOrderCreate2Operation(
            owner=str(self.app.world.profile_data.name),
            order_id=int(self.__order_id_input.value),
            fill_or_kill=bool(self.__fill_or_kill_input.value),
            expiration=self.__expiration_input.value,
            amount_to_sell=self.__currency_selector_amount_to_sell.selected.value(
                float(self.__amount_to_sell_input.value)
            ),
            exchange_rate=exchange_rate,
        )
