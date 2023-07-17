from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.operation_base import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.currency_selector import CurrencySelectorLiquid
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import LimitOrderCreate2Operation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from schemas.__private.hive_fields_basic_schemas import AssetHbdHF26, AssetHiveHF26


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class ExchangeRatePlaceTaker(Static):
    """Container used for making correct layout of Exchange rate big title."""


class BaseQuotePlaceTaker(Static):
    """Container used for making correct layout of base and quote fields."""


class AmountToSellPlaceTaker(Static):
    """Container used for making correct layout of amount to sell field."""


class LimitOrderCreate2(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        default_fill_or_kill = str(get_default_from_model(LimitOrderCreate2Operation, "fill_or_kill"))
        default_order_id = str(0)

        self.__order_id_input = Input(default_order_id, placeholder="e.g.: 1000")
        self.__fill_or_kill_input = Input(default_fill_or_kill, placeholder="e.g.: True")
        self.__expiration_input = Input(placeholder="e.g.: 2023-01-01T00:00:00")
        self.__amount_to_sell_input = Input(placeholder="e.g.: 1.000")
        self.__base_input = Input(placeholder="e.g: 1")
        self.__quote_input = Input(placeholder="e.g: 10")
        self.__currency_selector_amount_to_sell = CurrencySelectorLiquid()
        self.__currency_selector_base = CurrencySelectorLiquid()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Limit order create two")
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

    def _create_operation(self) -> LimitOrderCreate2Operation[AssetHbdHF26, AssetHiveHF26]:
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
