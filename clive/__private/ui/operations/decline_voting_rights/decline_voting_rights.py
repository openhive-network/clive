from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ValidationError
from textual.binding import Binding
from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.notification import Notification
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import DeclineVotingRightsOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class DeclineVotingRights(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

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

    def create_operation(self) -> Operation | None:
        try:
            return DeclineVotingRightsOperation(
                account=self.__account_input.value, decline=bool(self.__decline_input.value)
            )
        except ValidationError as error:
            Notification(f"Operation failed the validation process.\n{error}", category="error").show()
            return None
