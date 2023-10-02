from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer
from textual.widgets import Static

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.inputs.fee_input import FeeInput
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.inputs.witness_input import WitnessInput
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import WitnessSetPropertiesOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class WitnessSetProperties(RawOperationBaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self) -> None:
        super().__init__()

        self.__witness_input = WitnessInput()
        self.__account_creation_fee_input = FeeInput(label="account creation fee")
        self.__maximum_block_size_input = IntegerInput(
            label="maximum block size", value=131072, placeholder="maximum block size"
        )
        self.__hbd_interest_rate_input = IntegerInput(
            label="hbd interest rate", value=1000, placeholder="hbd interest rate"
        )

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Witness set properties")
            with ScrollableContainer(), Body():
                yield from self.__witness_input.compose()
                yield BigTitle("Props")
                yield PlaceTaker()
                yield from self.__account_creation_fee_input.compose()
                yield from self.__maximum_block_size_input.compose()
                yield from self.__hbd_interest_rate_input.compose()

    def _create_operation(self) -> WitnessSetPropertiesOperation | None:
        account_creation_fee = self.__account_creation_fee_input.value
        max_block_size = self.__maximum_block_size_input.value
        hbd_interest_rate = self.__hbd_interest_rate_input.value
        if not account_creation_fee or not max_block_size or not hbd_interest_rate:
            return None

        props_field = {
            "account_creation_fee": Asset.hive(account_creation_fee),
            "maximum_block_size": max_block_size,
            "hbd_interest_rate": hbd_interest_rate,
        }

        return WitnessSetPropertiesOperation(witness=self.__witness_input.value, props=props_field)
