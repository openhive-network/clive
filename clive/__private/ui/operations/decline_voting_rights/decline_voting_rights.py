from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.cart_based_screen.cart_based_screen import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import DeclineVotingRightsOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class DeclineVotingRights(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        self.__account_input = Input(placeholder="e.g.: alice")
        self.__decline_input = Input(value="True-")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Decline voting rights")
            with Body():
                yield Static("account", classes="label")
                yield self.__account_input
                yield Static("decline", classes="label")
                yield self.__decline_input

    def _create_operation(self) -> Operation | None:
        return DeclineVotingRightsOperation(
            account=self.__account_input.value, decline=bool(self.__decline_input.value)
        )
