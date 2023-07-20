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
from schemas.operations import LimitOrderCreateOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Asset


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class LimitOrderCreate(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        default_order_id = str(get_default_from_model(LimitOrderCreateOperation, "orderid", int))
        default_fill_or_kill = get_default_from_model(LimitOrderCreateOperation, "fill_or_kill", bool)

        self.__order_id_input = Input(default_order_id, placeholder=ID_PLACEHOLDER)
        self.__amount_to_sell_input = Input(placeholder=ASSET_AMOUNT_PLACEHOLDER)
        self.__min_to_receive_input = Input(placeholder=ASSET_AMOUNT_PLACEHOLDER)
        self.__fill_or_kill_input = Checkbox("fill or kill", value=default_fill_or_kill)
        self.__expiration_input = Input(placeholder=DATE_PLACEHOLDER)
        self.__currency_selector_to_sell = CurrencySelectorLiquid()
        self.__currency_selector_to_receive = CurrencySelectorLiquid()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Limit order create")
            with Body():
                yield Static("owner", classes="label")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="owner-label")
                yield PlaceTaker()
                yield Static("order id", classes="label")
                yield self.__order_id_input
                yield Static("expiration", classes="label")
                yield self.__expiration_input
                yield Static("amount to sell", classes="label")
                yield self.__amount_to_sell_input
                yield self.__currency_selector_to_sell
                yield Static("min to receive", classes="label")
                yield self.__min_to_receive_input
                yield self.__currency_selector_to_receive
                yield self.__fill_or_kill_input

    def _create_operation(self) -> LimitOrderCreateOperation[Asset.Hive, Asset.Hbd]:
        return LimitOrderCreateOperation(
            owner=self.app.world.profile_data.name,
            orderid=int(self.__order_id_input.value),
            amount_to_sell=self.__currency_selector_to_sell.selected.value(self.__amount_to_sell_input.value),
            min_to_receive=self.__currency_selector_to_receive.selected.value(self.__min_to_receive_input.value),
            fill_or_kill=bool(self.__fill_or_kill_input.value),
            expiration=self.__expiration_input.value,
        )
