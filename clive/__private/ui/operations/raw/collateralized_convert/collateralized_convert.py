from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.placeholders_constants import ASSET_AMOUNT_PLACEHOLDER, ID_PLACEHOLDER
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import CollateralizedConvertOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class CollateralizedConvert(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        default_request_id = str(get_default_from_model(CollateralizedConvertOperation, "request_id", int))

        self.__amount_input = CustomInput(label="amount", placeholder=ASSET_AMOUNT_PLACEHOLDER)
        self.__request_id_input = CustomInput(label="request id", value=default_request_id, placeholder=ID_PLACEHOLDER)

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Collateralized convert")
            with Body():
                yield InputLabel("owner")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="owner-label")
                yield from self.__request_id_input.compose()
                yield from self.__amount_input.compose()

    def _create_operation(self) -> CollateralizedConvertOperation[Asset.Hive]:
        return CollateralizedConvertOperation(
            owner=self.app.world.profile_data.working_account.name,
            request_id=int(self.__request_id_input.value),
            amount=Asset.hive(self.__amount_input.value),
        )
