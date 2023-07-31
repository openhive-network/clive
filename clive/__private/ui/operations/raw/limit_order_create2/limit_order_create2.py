from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Checkbox, Input, Static

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.currency_selector import CurrencySelectorLiquid
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.placeholders_constants import (
    ASSET_AMOUNT_PLACEHOLDER,
    DATE_PLACEHOLDER,
    ID_PLACEHOLDER,
)
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import LimitOrderCreate2Operation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class LimitOrderCreate2(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        default_fill_or_kill = get_default_from_model(LimitOrderCreate2Operation, "fill_or_kill", bool)
        default_order_id = str(0)

        self.__order_id_input = Input(default_order_id, placeholder=ID_PLACEHOLDER)
        self.__fill_or_kill_input = Checkbox("fill or kill", value=default_fill_or_kill)
        self.__expiration_input = Input(placeholder=DATE_PLACEHOLDER)
        self.__amount_to_sell_input = Input(placeholder=ASSET_AMOUNT_PLACEHOLDER)
        self.__base_input = Input(placeholder=ASSET_AMOUNT_PLACEHOLDER)
        self.__quote_input = Input(placeholder=ASSET_AMOUNT_PLACEHOLDER)
        self.__currency_selector_amount_to_sell = CurrencySelectorLiquid()
        self.__currency_selector_base = CurrencySelectorLiquid()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Limit order create two")
            with Body():
                yield Static("owner", classes="label")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="owner-label")
                yield PlaceTaker(id="first-taker")
                yield Static("order id", classes="label")
                yield self.__order_id_input
                yield Static("", classes="label")
                yield self.__fill_or_kill_input
                yield Static("expiration", classes="label")
                yield self.__expiration_input
                yield PlaceTaker()
                yield Static("amount to sell", classes="label")
                yield self.__amount_to_sell_input
                yield self.__currency_selector_amount_to_sell
                yield PlaceTaker()
                yield BigTitle("Exchange rate")
                yield PlaceTaker()
                yield Static("base", classes="label")
                yield self.__base_input
                yield self.__currency_selector_base
                yield Static("quote", classes="label")
                yield self.__quote_input

    def _create_operation(self) -> LimitOrderCreate2Operation[Asset.Hbd, Asset.Hive]:
        exchange_rate = {
            "base": self.__currency_selector_base.create_asset(self.__base_input.value),
            "quote": Asset.hive(self.__quote_input.value),
        }

        return LimitOrderCreate2Operation(
            owner=self.app.world.profile_data.name,
            order_id=int(self.__order_id_input.value),
            fill_or_kill=self.__fill_or_kill_input.value,
            expiration=self.__expiration_input.value,
            amount_to_sell=self.__currency_selector_amount_to_sell.create_asset(self.__amount_to_sell_input.value),
            exchange_rate=exchange_rate,
        )
