from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer
from textual.widgets import Checkbox, Static

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.amount_input import AmountInput
from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.inputs.id_input import IdInput, OrderIdT
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.placeholders_constants import (
    ASSET_AMOUNT_PLACEHOLDER,
    DATE_PLACEHOLDER,
)
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import LimitOrderCreate2Operation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class LimitOrderCreate2(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        default_fill_or_kill = get_default_from_model(LimitOrderCreate2Operation, "fill_or_kill", bool)
        default_order_id = 0

        self.__order_id_input = IdInput[OrderIdT](label="order id", value=default_order_id)
        self.__fill_or_kill_input = Checkbox("fill or kill", value=default_fill_or_kill)
        self.__expiration_input = CustomInput(label="expiration", placeholder=DATE_PLACEHOLDER)
        self.__amount_to_sell_input = AmountInput()
        self.__base_input = AmountInput()
        self.__quote_input = CustomInput(label="quote", placeholder=ASSET_AMOUNT_PLACEHOLDER)

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Limit order create two")
            with ScrollableContainer(), Body():
                yield InputLabel("owner")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="owner-label")
                yield from self.__order_id_input.compose()
                yield Static("")
                yield self.__fill_or_kill_input
                yield from self.__expiration_input.compose()
                yield InputLabel("amount to sell")
                yield self.__amount_to_sell_input
                yield Static("")
                yield BigTitle("Exchange rate")
                yield InputLabel("base")
                yield self.__base_input
                yield from self.__quote_input.compose()

    def _create_operation(self) -> LimitOrderCreate2Operation[Asset.Hbd, Asset.Hive] | None:
        base = self.__base_input.amount

        exchange_rate = {
            "base": base,
            "quote": Asset.hive(self.__quote_input.value),
        }

        amount_to_sell = self.__amount_to_sell_input.amount

        if not amount_to_sell or not base:
            return None

        return LimitOrderCreate2Operation(
            owner=self.app.world.profile_data.name,
            order_id=int(self.__order_id_input.value),
            fill_or_kill=self.__fill_or_kill_input.value,
            expiration=self.__expiration_input.value,
            amount_to_sell=amount_to_sell,
            exchange_rate=exchange_rate,
        )
