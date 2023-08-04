from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Static

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.placeholders_constants import ASSET_AMOUNT_PLACEHOLDER
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
    def __init__(self) -> None:
        super().__init__()

        self.__witness_input = AccountNameInput(label="witness")
        self.__account_creation_fee_input = CustomInput(
            label="account creation fee", placeholder=ASSET_AMOUNT_PLACEHOLDER
        )
        self.__maximum_block_size_input = CustomInput(
            label="maximum block size", default_value="131072", placeholder="maximum block size"
        )
        self.__hbd_interest_rate_input = CustomInput(
            label="hbd interest rate", default_value="1000", placeholder="hbd interest rate"
        )

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Witness set properties")
            with Body():
                yield from self.__witness_input.compose()
                yield BigTitle("Props")
                yield PlaceTaker()
                yield from self.__account_creation_fee_input.compose()
                yield from self.__maximum_block_size_input.compose()
                yield from self.__hbd_interest_rate_input.compose()

    def _create_operation(self) -> WitnessSetPropertiesOperation:
        props_field = {
            "account_creation_fee": Asset.hive(self.__account_creation_fee_input.value),
            "maximum_block_size": int(self.__maximum_block_size_input.value),
            "hbd_interest_rate": int(self.__hbd_interest_rate_input.value),
        }

        return WitnessSetPropertiesOperation(witness=self.__witness_input.value, props=props_field)
