from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.cart_based_screen.cart_based_screen import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import ResetAccountOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class ResetAccount(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        self.__reset_account_input = Input(placeholder="e.g: alice")
        self.__account_to_reset_input = Input(placeholder="e.g: bob")
        self.__weight_threshold_input = Input(placeholder="e.g: 1")
        self.__account_auths_input = Input(placeholder="e.g: alice, 1; bob, 1. Notice: remove pair of values by ;")
        self.__key_auths_input = Input(
            placeholder="e.g: STM6vJmrwaX5TjgTS9dPH8KsArso5m91fVodJvv91j7G765wqcNM9, 1. "
            "Notice: remove pair of values by ;"
        )

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Reset account")
            with Body():
                yield Static("reset account", classes="label")
                yield self.__reset_account_input
                yield Static("account to reset", classes="label")
                yield self.__account_to_reset_input
                yield BigTitle("New owner authority", classes="authority-label")
                yield PlaceTaker()
                yield Static("weight threshold", classes="label")
                yield self.__weight_threshold_input
                yield Static("account auths", classes="label")
                yield self.__account_auths_input
                yield Static("key auths", classes="label")
                yield self.__key_auths_input

    def _create_operation(self) -> Operation | None:
        valid_account_auths = OperationBase._split_auths_fields(self.__account_auths_input.value)
        split_key_auths = OperationBase._split_auths_fields(self.__key_auths_input.value)

        authority_field = {
            "weight_threshold": int(self.__weight_threshold_input.value),
            "account_auths": valid_account_auths,
            "key_auths": split_key_auths,
        }

        return ResetAccountOperation(
            reset_account=self.__reset_account_input.value,
            account_to_reset=self.__account_to_reset_input.value,
            new_owner_authority=authority_field,
        )
