from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.placeholders_constants import ID_PLACEHOLDER
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import LimitOrderCancelOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class LimitOrderCancel(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        default_order_id = str(get_default_from_model(LimitOrderCancelOperation, "order_id", int))

        self.__order_id_input = CustomInput(label="order id", value=default_order_id, placeholder=ID_PLACEHOLDER)

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Limit order cancel")
            with ScrollableContainer(), Body():
                yield InputLabel("owner")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="owner-label")
                yield from self.__order_id_input.compose()

    def _create_operation(self) -> LimitOrderCancelOperation:
        return LimitOrderCancelOperation(
            owner=self.app.world.profile_data.working_account.name,
            order_id=int(self.__order_id_input.value),
        )
