from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.placeholders_constants import (
    ACCOUNT_AUTHS_PLACEHOLDER,
    ACCOUNT_NAME_PLACEHOLDER,
    KEY_AUTHS_PLACEHOLDER,
    WEIGHT_THRESHOLD_PLACEHOLDER,
)
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import RecoverAccountOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of new owner authority."""


class RecoverAccount(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        self.__account_to_recover_input = Input(placeholder=ACCOUNT_NAME_PLACEHOLDER)
        self.__weight_threshold_new_input = Input(placeholder=WEIGHT_THRESHOLD_PLACEHOLDER)
        self.__account_auths_new_input = Input(placeholder=ACCOUNT_AUTHS_PLACEHOLDER)
        self.__key_auths_new_input = Input(placeholder=KEY_AUTHS_PLACEHOLDER)
        self.__weight_threshold_recent_input = Input(placeholder=WEIGHT_THRESHOLD_PLACEHOLDER)
        self.__account_auths_recent_input = Input(placeholder=ACCOUNT_AUTHS_PLACEHOLDER)
        self.__key_auths_recent_input = Input(placeholder=KEY_AUTHS_PLACEHOLDER)

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Recover account")
            with Body():
                yield Static("account to recover", classes="label")
                yield self.__account_to_recover_input
                yield PlaceTaker()
                yield BigTitle("New owner authority")
                yield Static("weight threshold", classes="label")
                yield self.__weight_threshold_new_input
                yield Static("account auths", classes="label")
                yield self.__account_auths_new_input
                yield Static("key auths", classes="label")
                yield self.__key_auths_new_input
                yield PlaceTaker()
                yield BigTitle("Recent owner authority")
                yield Static("weight threshold", classes="label")
                yield self.__weight_threshold_recent_input
                yield Static("account auths", classes="label")
                yield self.__account_auths_recent_input
                yield Static("key auths", classes="label")
                yield self.__key_auths_recent_input

    def _create_operation(self) -> RecoverAccountOperation:
        new_owner_authority = self._create_authority_field(
            self.__weight_threshold_new_input, self.__account_auths_new_input, self.__key_auths_new_input
        )

        recent_owner_authority = self._create_authority_field(
            self.__weight_threshold_recent_input, self.__account_auths_recent_input, self.__key_auths_recent_input
        )

        return RecoverAccountOperation(
            account_to_recover=self.__account_to_recover_input.value,
            new_owner_authority=new_owner_authority,
            recent_owner_authority=recent_owner_authority,
        )
