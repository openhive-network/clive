from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.id_input import IdInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.numeric_input import NumericInput
from clive.models import Asset
from schemas.operations import ConvertOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class Convert(RawOperationBaseScreen):
    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self) -> None:
        super().__init__()

        default_request_id = get_default_from_model(ConvertOperation, "request_id", int)

        self.__request_id_input = IdInput(label="request id", value=default_request_id)
        self.__amount_input = NumericInput(label="amount hbd")

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Convert")
        with ScrollableContainer(), Body():
            yield InputLabel("from")
            yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="from-label")
            yield from self.__request_id_input.compose()
            yield from self.__amount_input.compose()

    def _create_operation(self) -> ConvertOperation | None:
        request_id = self.__request_id_input.value
        amount = self.__amount_input.value

        if not request_id or not amount:
            return None

        return ConvertOperation(
            from_=self.app.world.profile_data.working_account.name,
            request_id=request_id,
            amount=Asset.hbd(amount),
        )
