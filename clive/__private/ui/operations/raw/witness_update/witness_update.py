from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer
from textual.widgets import Static

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.fee_input import FeeInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import KEY_PLACEHOLDER
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import WitnessUpdateOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class WitnessUpdate(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        self.__url_input = TextInput(self, label="url", placeholder="e.g: witness-category/my-witness")
        self.__block_signing_key_input = TextInput(self, label="block signing key", placeholder=KEY_PLACEHOLDER)
        self.__account_creation_fee_input = FeeInput(self, label="account creation fee")
        self.__maximum_block_size_input = IntegerInput(
            self, label="maximum block size", value=131072, placeholder="maximum block size"
        )
        self.__hbd_interest_rate_input = IntegerInput(
            self, label="hbd interest rate", value=1000, placeholder="hbd interest rate"
        )
        self.__fee_input = FeeInput(self)

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
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

    def _create_operation(self) -> WitnessUpdateOperation[Asset.Hive]:
        props_field = {
            "account_creation_fee": Asset.hive(self.__account_creation_fee_input.value),
            "maximum_block_size": self.__maximum_block_size_input.value,
            "hbd_interest_rate": self.__hbd_interest_rate_input.value,
        }

        return WitnessUpdateOperation(
            owner=self.app.world.profile_data.name,
            url=self.__url_input.value,
            block_signing_key=self.__block_signing_key_input.value,
            props=props_field,
            fee=Asset.hive(self.__fee_input.value),
        )
