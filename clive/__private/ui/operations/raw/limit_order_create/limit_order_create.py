from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer
from textual.widgets import Checkbox

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.asset_amount_input import AssetAmountInput
from clive.__private.ui.widgets.inputs.date_input import DateInput
from clive.__private.ui.widgets.inputs.id_input import IdInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import LimitOrderCreateOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Asset


class Body(Grid):
    """All the content of the screen, excluding the title."""


class LimitOrderCreate(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        default_order_id = get_default_from_model(LimitOrderCreateOperation, "orderid", int)
        default_fill_or_kill = get_default_from_model(LimitOrderCreateOperation, "fill_or_kill", bool)

        self.__order_id_input = IdInput(label="order id", value=default_order_id)
        self.__amount_to_sell_input = AssetAmountInput()
        self.__min_to_receive_input = AssetAmountInput()
        self.__fill_or_kill_input = Checkbox("fill or kill", value=default_fill_or_kill)
        self.__expiration_input = DateInput(label="expiration")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Limit order create")
            with ScrollableContainer(), Body():
                yield InputLabel("owner")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="owner-label")
                yield from self.__order_id_input.compose()
                yield from self.__expiration_input.compose()
                yield from self.__amount_to_sell_input.compose()
                yield from self.__min_to_receive_input.compose()
                yield self.__fill_or_kill_input

    def _create_operation(self) -> LimitOrderCreateOperation[Asset.Hive, Asset.Hbd] | None:
        asset_to_sell = self.__amount_to_sell_input.value
        asset_min_receive = self.__min_to_receive_input.value

        if not asset_to_sell or not asset_min_receive:
            return None

        return LimitOrderCreateOperation(
            owner=self.app.world.profile_data.name,
            orderid=self.__order_id_input.value,
            amount_to_sell=asset_to_sell,
            min_to_receive=asset_min_receive,
            fill_or_kill=bool(self.__fill_or_kill_input.value),
            expiration=self.__expiration_input.value,
        )
