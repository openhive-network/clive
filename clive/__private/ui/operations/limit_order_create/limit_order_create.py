from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.operation_base import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.currency_selector_liquid import CurrencySelectorLiquid
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import LimitOrderCreateOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from schemas.__private.hive_fields_basic_schemas import AssetHbdHF26, AssetHiveHF26


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class LimitOrderCreate(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        default_order_id = str(get_default_from_model(LimitOrderCreateOperation, "order_id"))
        default_fill_or_kill = str(get_default_from_model(LimitOrderCreateOperation, "fill_or_kill"))

        self.__order_id_input = Input(default_order_id, placeholder="e.g.: 1000")
        self.__amount_to_sell_input = Input(placeholder="e.g.: 1.000")
        self.__min_to_receive_input = Input(placeholder="e.g.: 1.000")
        self.__fill_or_kill_input = Input(default_fill_or_kill, placeholder="e.g.: True")
        self.__time_point_sec_input = Input(placeholder="e.g.: 1970-01-01T00:00:00")
        self.__currency_selector_to_sell = CurrencySelectorLiquid()
        self.__currency_selector_to_receive = CurrencySelectorLiquid()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Limit order create")
            with Body():
                yield Static("owner", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="owner-label")
                yield PlaceTaker()
                yield Static("order id", classes="label")
                yield self.__order_id_input
                yield Static("fill or kill", classes="label")
                yield self.__fill_or_kill_input
                yield Static("time point sec", classes="label")
                yield self.__time_point_sec_input
                yield Static("amount to sell", classes="label")
                yield self.__amount_to_sell_input
                yield self.__currency_selector_to_sell
                yield Static("min to receive", classes="label")
                yield self.__min_to_receive_input
                yield self.__currency_selector_to_receive

    def _create_operation(self) -> LimitOrderCreateOperation[AssetHiveHF26, AssetHbdHF26]:
        return LimitOrderCreateOperation(
            owner=str(self.app.world.profile_data.name),
            order_id=int(self.__order_id_input.value),
            amount_to_sell=self.__currency_selector_to_sell.selected.value(float(self.__amount_to_sell_input.value)),
            min_to_receive=self.__currency_selector_to_receive.selected.value(float(self.__min_to_receive_input.value)),
            fill_or_kill=bool(self.__fill_or_kill_input.value),
            time_point_sec=self.__time_point_sec_input.value,
        )
