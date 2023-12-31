from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer
from textual.widgets import Static

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.fee_input import FeeInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import KEY_PLACEHOLDER
from clive.models import Asset
from schemas.operations import WitnessUpdateOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class WitnessUpdate(RawOperationBaseScreen):
    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__url_input = TextInput(label="url", placeholder="e.g: witness-category/my-witness")
        self.__block_signing_key_input = TextInput(label="block signing key", placeholder=KEY_PLACEHOLDER)
        self.__account_creation_fee_input = FeeInput(label="account creation fee")
        self.__maximum_block_size_input = IntegerInput(
            label="maximum block size", value=131072, placeholder="maximum block size"
        )
        self.__hbd_interest_rate_input = IntegerInput(
            label="hbd interest rate", value=1000, placeholder="hbd interest rate"
        )
        self.__fee_input = FeeInput()

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Witness update")
        with ScrollableContainer(), Body():
            yield InputLabel("owner")
            yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="owner-label")
            yield from self.__url_input.compose()
            yield from self.__block_signing_key_input.compose()
            yield from self.__fee_input.compose()
            yield BigTitle("Props")
            yield PlaceTaker()
            yield from self.__account_creation_fee_input.compose()
            yield from self.__maximum_block_size_input.compose()
            yield from self.__hbd_interest_rate_input.compose()

    def _create_operation(self) -> WitnessUpdateOperation | None:
        fee = self.__fee_input.value
        creation_fee = self.__account_creation_fee_input.value
        max_block_size = self.__maximum_block_size_input.value
        hbd_interest_rate = self.__hbd_interest_rate_input.value
        if not fee or not max_block_size or not hbd_interest_rate or not creation_fee:
            return None

        props_field = {
            "account_creation_fee": Asset.hive(creation_fee),
            "maximum_block_size": max_block_size,
            "hbd_interest_rate": hbd_interest_rate,
        }

        return WitnessUpdateOperation(
            owner=self.app.world.profile_data.working_account.name,
            url=self.__url_input.value,
            block_signing_key=self.__block_signing_key_input.value,
            props=props_field,
            fee=Asset.hive(fee),
        )
