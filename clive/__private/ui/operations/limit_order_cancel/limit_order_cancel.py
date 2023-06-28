from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.cart_based_screen.cart_based_screen import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import LimitOrderCancelOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation


class Body(Grid):
    """All the content of the screen, excluding the title"""


class LimitOrderCancel(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        self.__order_id_input = Input(placeholder="e.g.: 2000. Notice: default value is 0")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Limit order cancel")
            with Body():
                yield Static("owner", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="owner-label")
                yield Static("order_id", classes="label")
                yield self.__order_id_input

    def _create_operation(self) -> Operation | None:
        return LimitOrderCancelOperation(
            owner=str(self.app.world.profile_data.working_account.name),
            order_id=int(self.__order_id_input.value),
        )
