from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.inputs.id_input import IdInput, RequestIdT
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.placeholders_constants import ASSET_AMOUNT_PLACEHOLDER
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import ConvertOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class Convert(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        default_request_id = get_default_from_model(ConvertOperation, "request_id", int)

        self.__request_id_input = IdInput[RequestIdT](label="request id", value=default_request_id)
        self.__amount_input = CustomInput(label="amount", placeholder=ASSET_AMOUNT_PLACEHOLDER)

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Convert")
            with ScrollableContainer(), Body():
                yield InputLabel("from")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="from-label")
                yield from self.__request_id_input.compose()
                yield from self.__amount_input.compose()

    def _create_operation(self) -> ConvertOperation[Asset.Hbd]:
        return ConvertOperation(
            from_=self.app.world.profile_data.working_account.name,
            request_id=int(self.__request_id_input.value),
            amount=Asset.hbd(self.__amount_input.value),
        )
