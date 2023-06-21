from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ValidationError
from textual.binding import Binding
from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.notification import Notification
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import AccountWitnessVoteOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class AccountWitnessVote(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__witness_input = Input(placeholder="e.g.: hiveio")
        self.__approve_input = Input(placeholder="e.g.: True. Notice - default value is True")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Account witness vote")
            with Body():
                yield Static("account", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="account-label")
                yield PlaceTaker()
                yield Static("witness", classes="label")
                yield self.__witness_input
                yield Static("approve", classes="label")
                yield self.__approve_input

    def create_operation(self) -> Operation | None:
        try:
            if self.__approve_input.value:
                """Default value of approve is True, so if empty auto-fill with this"""
                return AccountWitnessVoteOperation(
                    account=str(self.app.world.profile_data.working_account.name),
                    witness=self.__witness_input.value,
                    approve=self.__approve_input.value,
                )
            return AccountWitnessVoteOperation(  # noqa: TRY300
                account=str(self.app.world.profile_data.working_account.name),
                witness=self.__witness_input.value,
            )

        except ValidationError as error:
            Notification(f"Operation failed the validation process.\n{error}", category="error").show()
            return None
