from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.operation_base import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import LimitOrderCancelOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class LimitOrderCancel(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        default_order_id = str(get_default_from_model(LimitOrderCancelOperation, "order_id"))

        self.__order_id_input = Input(default_order_id, placeholder="e.g.: 2000")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Limit order cancel")
            with Body():
                yield Static("owner", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="owner-label")
                yield Static("order_id", classes="label")
                yield self.__order_id_input

    def _create_operation(self) -> LimitOrderCancelOperation:
        return LimitOrderCancelOperation(
            owner=str(self.app.world.profile_data.working_account.name),
            order_id=int(self.__order_id_input.value),
        )
