from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.cart_based_screen.cart_based_screen import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import EscrowDisputeOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid"""


class EscrowDispute(OperationBase):
    def __init__(self) -> None:
        super().__init__()
        self.__to_input = Input(placeholder="e.g: bob")
        self.__agent_input = Input(placeholder="e.g: charlie")
        self.__who_input = Input(placeholder="e.g: charlie")
        self.__escrow_id_input = Input(placeholder="e.g.: 23456789. Notice - default is 30")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Escrow dispute")
            with Body():
                yield Static("from", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="from-label")
                yield PlaceTaker()
                yield Static("to", classes="label")
                yield self.__to_input
                yield Static("agent", classes="label")
                yield self.__agent_input
                yield Static("who", classes="label")
                yield self.__who_input
                yield Static("escrow id", classes="label")
                yield self.__escrow_id_input

    def _create_operation(self) -> Operation | None:
        return EscrowDisputeOperation(
            from_=str(self.app.world.profile_data.name),
            to=self.__to_input.value,
            agent=self.__agent_input.value,
            escrow_id=int(self.__escrow_id_input.value),
            who=self.__who_input.value,
        )
