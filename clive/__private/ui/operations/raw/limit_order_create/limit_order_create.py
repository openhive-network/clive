from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Checkbox

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.amount_input import AmountInput
from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.placeholders_constants import (
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


class LimitOrderCreate(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        default_order_id = str(get_default_from_model(LimitOrderCreateOperation, "orderid", int))
        default_fill_or_kill = get_default_from_model(LimitOrderCreateOperation, "fill_or_kill", bool)

        self.__order_id_input = CustomInput(
            label="order id", default_value=default_order_id, placeholder=ID_PLACEHOLDER
        )
        self.__amount_to_sell_input = AmountInput()
        self.__min_to_receive_input = AmountInput()
        self.__fill_or_kill_input = Checkbox("fill or kill", value=default_fill_or_kill)
        self.__expiration_input = CustomInput(label="expiration", placeholder=DATE_PLACEHOLDER)

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Limit order create")
            with Body():
                yield InputLabel("owner")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="owner-label")
                yield from self.__order_id_input.compose()
                yield from self.__expiration_input.compose()
                yield from self.__amount_to_sell_input.compose()
                yield from self.__min_to_receive_input.compose()
                yield self.__fill_or_kill_input

    def _create_operation(self) -> LimitOrderCreateOperation[Asset.Hive, Asset.Hbd] | None:
        asset_to_sell = self.__amount_to_sell_input.amount
        asset_min_receive = self.__min_to_receive_input.amount

        if not asset_to_sell or not asset_min_receive:
            return None

        return LimitOrderCreateOperation(
            owner=self.app.world.profile_data.name,
            orderid=int(self.__order_id_input.value),
            amount_to_sell=asset_to_sell,
            min_to_receive=asset_min_receive,
            fill_or_kill=bool(self.__fill_or_kill_input.value),
            expiration=self.__expiration_input.value,
        )
