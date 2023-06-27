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
from clive.models import Asset, Operation
from schemas.operations import ClaimRewardBalanceOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class ClaimRewardBalance(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__reward_hive_input = Input(placeholder="e.g.: 1.000")
        self.__reward_hbd_input = Input(placeholder="e.g.: 2.000")
        self.__reward_vests_input = Input(placeholder="e.g.: 3.000")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Claim reward balance")
            with Body():
                yield Static("account", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="account-label")
                yield PlaceTaker()
                yield Static("reward hive", classes="label")
                yield self.__reward_hive_input
                yield Static("reward hbd", classes="label")
                yield self.__reward_hbd_input
                yield Static("reward vests", classes="label")
                yield self.__reward_vests_input

    def create_operation(self) -> Operation | None:
        try:
            return ClaimRewardBalanceOperation(
                account=str(self.app.world.profile_data.name),
                reward_hive=Asset.hive(float(self.__reward_hive_input.value)),
                reward_hbd=Asset.hbd(float(self.__reward_hbd_input.value)),
                reward_vests=Asset.vests(float(self.__reward_vests_input.value)),
            )
        except ValidationError as error:
            Notification(f"Operation failed the validation process.\n{error}", category="error").show()
            return None
