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
from schemas.operations import SetWithdrawVestingRouteOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class SetWithdrawVestingRoute(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__to_account_input = Input(placeholder="e.g.: alice")
        self.__percent_input = Input(placeholder="e.g.: 10. Notice: default value is 0")
        self.__auto_vest_input = Input(placeholder="e.g. True. Notice: default is False")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Set withdraw vesting route")
            with Body():
                yield Static("from", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="from-label")
                yield PlaceTaker()
                yield Static("to account", classes="label")
                yield self.__to_account_input
                yield Static("percent", classes="label")
                yield self.__percent_input
                yield Static("auto vest", classes="label")
                yield self.__auto_vest_input

    def create_operation(self) -> Operation | None:
        try:
            if self.__auto_vest_input.value and self.__percent_input.value:
                return SetWithdrawVestingRouteOperation(
                    from_account=str(self.app.world.profile_data.name),
                    to_account=self.__to_account_input.value,
                    auto_vest=bool(self.__auto_vest_input.value),
                    percent=int(self.__percent_input.value),
                )
            elif self.__auto_vest_input.value or self.__percent_input.value:  # noqa: RET505
                return (
                    SetWithdrawVestingRouteOperation(
                        from_account=str(self.app.world.profile_data.name),
                        to_account=self.__to_account_input.value,
                        auto_vest=bool(self.__auto_vest_input.value),
                    )
                    if self.__auto_vest_input.value
                    else SetWithdrawVestingRouteOperation(
                        from_account=str(self.app.world.profile_data.name),
                        to_account=self.__to_account_input.value,
                        percent=int(self.__percent_input.value),
                    )
                )
            return SetWithdrawVestingRouteOperation(  # noqa: TRY300
                from_account=str(self.app.world.profile_data.name),
                to_account=self.__to_account_input.value,
            )

        except ValidationError as error:
            Notification(f"Operation failed the validation process.\n{error}", category="error").show()
            return None
