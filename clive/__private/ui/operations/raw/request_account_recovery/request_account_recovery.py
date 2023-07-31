from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.inputs.account_auths_input import AccountAuthsInput
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.key_auths_input import KeyAuthsInput
from clive.__private.ui.widgets.placeholders_constants import (
    ACCOUNT_NAME2_PLACEHOLDER,
    WEIGHT_THRESHOLD_PLACEHOLDER,
)
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import RequestAccountRecoveryOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class RequestAccountRecovery(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        self.__recovery_account_input = AccountNameInput(label="recovery account")
        self.__account_to_recover_input = AccountNameInput(
            label="account to recover", placeholder=ACCOUNT_NAME2_PLACEHOLDER
        )
        self.__weight_threshold_input = Input(placeholder=WEIGHT_THRESHOLD_PLACEHOLDER)
        self.__account_auths_input = AccountAuthsInput(label="account auths")
        self.__key_auths_input = KeyAuthsInput(label="key auths")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Request account recovery")
            with Body():
                yield from self.__recovery_account_input.compose()
                yield from self.__account_to_recover_input.compose()
                yield PlaceTaker()
                yield BigTitle("New owner authority")
                yield Static("weight threshold", classes="label")
                yield self.__weight_threshold_input
                yield from self.__account_auths_input.compose()
                yield from self.__key_auths_input.compose()

    def _create_operation(self) -> RequestAccountRecoveryOperation:
        new_owner_authority = self._create_authority_field(
            self.__weight_threshold_input, self.__account_auths_input, self.__key_auths_input
        )

        return RequestAccountRecoveryOperation(
            recovery_account=self.__recovery_account_input.value,
            account_to_recover=self.__account_to_recover_input.value,
            new_owner_authority=new_owner_authority,
        )
