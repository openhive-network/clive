from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ValidationError
from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.activate.activate import Activate
from clive.__private.ui.operations.cart import Cart
from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreenOperations
from clive.__private.ui.operations.tranaction_summary import TransactionSummary
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.notification import Notification
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.__private.hive_fields_basic_schemas import Int16t
from schemas.operations import VoteOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class Vote(CartBasedScreenOperations):
    def __init__(self) -> None:
        super().__init__()

        self.__author_input = Input(placeholder="e.g.: alice")
        self.__permlink_input = Input(placeholder="e.g.: a-post-by-alice")
        self.__weight_input = Input(placeholder="e.g.: 10000. Notice - default is 0")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Vote")
            with Body():
                yield Static("voter", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="voter-label")
                yield PlaceTaker()
                yield Static("author", classes="label")
                yield self.__author_input
                yield Static("permlink", classes="label")
                yield self.__permlink_input
                yield Static("weight", classes="label")
                yield self.__weight_input

    def on_activate_succeeded(self) -> None:
        self.__fast_broadcast()

    def action_finalize(self) -> None:
        if self.__add_to_cart():
            self.app.switch_screen(TransactionSummary())
            self.app.push_screen_at(-1, Cart())

    def action_add_to_cart(self) -> None:
        if self.__add_to_cart():
            self.app.pop_screen()

    def action_fast_broadcast(self) -> None:
        if not self.__create_operation():  # For faster validation feedback to the user
            return

        if not self.app.world.app_state.is_active():
            self.app.push_screen(Activate())
            return

        self.__fast_broadcast()

    def __fast_broadcast(self) -> None:
        if operation := self.__create_operation():
            self.app.world.commands.fast_broadcast(
                operation=operation, sign_with=self.app.world.profile_data.working_account.keys[0]
            )
            self.app.pop_screen()
            Notification(
                f"Operation `{operation.__class__.__name__}` broadcast succesfully.", category="success"
            ).show()

    def __create_operation(self) -> Operation | None:
        """
        Collects data from the screen and creates a new operation based on it.
        :return: Operation if the operation is valid, None otherwise.
        """

        try:
            if self.__weight_input.value:
                """Default value of weight is 0, so if empty auto-fill with this"""
                return VoteOperation(
                    voter=str(self.app.world.profile_data.working_account.name),
                    author=self.__author_input.value,
                    permlink=self.__permlink_input.value,
                    weight=Int16t(self.__weight_input.value),
                )
            return VoteOperation(  # noqa: TRY300
                voter=str(self.app.world.profile_data.working_account.name),
                author=self.__author_input.value,
                permlink=self.__permlink_input.value,
            )

        except ValidationError as error:
            Notification(f"Operation failed the validation process.\n{error}", category="error").show()
            return None

    def __add_to_cart(self) -> bool:
        """
        Creates a new operation and adds it to the cart.
        :return: True if the operation was added to the cart successfully, False otherwise.
        """
        operation = self.__create_operation()
        if not operation:
            return False

        self.app.world.profile_data.cart.append(operation)
        self.app.world.update_reactive("profile_data")
        return True
