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
from schemas.operations import RequestAccountRecoveryOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class RequestAccountRecovery(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__recovery_account_input = Input(placeholder="e.g: alice")
        self.__account_to_recover_input = Input(placeholder="e.g: bob")
        self.__weight_threshold_input = Input(placeholder="e.g: 1")
        self.__account_auths_input = Input(placeholder="e.g: alice, 1; bob, 1. Notice: split pair of values by ;")
        self.__key_auths_input = Input(
            placeholder="e.g: STM6vJmrwaX5TjgTS9dPH8KsArso5m91fVodJvv91j7G765wqcNM9, 1. "
            "Notice: split pair of values by ;"
        )

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Request account recovery")
            with Body():
                yield Static("recovery account", classes="label")
                yield self.__recovery_account_input
                yield Static("account to recover", classes="label")
                yield self.__account_to_recover_input
                yield BigTitle("New owner authority", classes="authority-label")
                yield PlaceTaker()
                yield Static("weight threshold", classes="label")
                yield self.__weight_threshold_input
                yield Static("account auths", classes="label")
                yield self.__account_auths_input
                yield Static("key auths", classes="label")
                yield self.__key_auths_input

    def create_operation(self) -> Operation | None:
        try:
            valid_account_auths = CartBasedScreen._split_auths_fields(self.__account_auths_input.value)
            split_key_auths = CartBasedScreen._split_auths_fields(self.__key_auths_input.value)

            authority_field = {
                "weight_threshold": int(self.__weight_threshold_input.value),
                "account_auths": valid_account_auths,
                "key_auths": split_key_auths,
            }

            return RequestAccountRecoveryOperation(  # noqa: TRY300
                recovery_account=self.__recovery_account_input.value,
                account_to_recover=self.__account_to_recover_input.value,
                new_owner_authority=authority_field,
            )
        except ValidationError as error:
            Notification(f"Operation failed the validation process.\n{error}", category="error").show()
            return None
