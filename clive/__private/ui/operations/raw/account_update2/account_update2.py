from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.placeholders_constants import (
    ACCOUNT_AUTHS_PLACEHOLDER,
    JSON_DATA_PLACEHOLDER,
    KEY_AUTHS_PLACEHOLDER,
    KEY_PLACEHOLDER,
    WEIGHT_THRESHOLD_PLACEHOLDER,
)
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import AccountUpdate2Operation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of owner authority part."""


class AccountUpdate2(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        self.__account_input = AccountNameInput(label="account")
        self.__memo_key_input = Input(placeholder=KEY_PLACEHOLDER)
        self.__json_metadata_input = Input(placeholder=JSON_DATA_PLACEHOLDER)
        self.__posting_json_metadata = Input(placeholder=JSON_DATA_PLACEHOLDER)

        self.__weight_threshold_owner_input = Input("", placeholder=WEIGHT_THRESHOLD_PLACEHOLDER)
        self.__account_auths_owner_input = Input("", placeholder=ACCOUNT_AUTHS_PLACEHOLDER)
        self.__key_auths_owner_input = Input(
            "",
            placeholder=KEY_AUTHS_PLACEHOLDER,
        )

        self.__weight_threshold_active_input = Input("", placeholder=WEIGHT_THRESHOLD_PLACEHOLDER)
        self.__account_auths_active_input = Input("", placeholder=ACCOUNT_AUTHS_PLACEHOLDER)
        self.__key_auths_active_input = Input(
            "",
            placeholder=KEY_AUTHS_PLACEHOLDER,
        )

        self.__weight_threshold_posting_input = Input("", placeholder=WEIGHT_THRESHOLD_PLACEHOLDER)
        self.__account_auths_posting_input = Input("", placeholder=ACCOUNT_AUTHS_PLACEHOLDER)
        self.__key_auths_posting_input = Input("", placeholder=KEY_AUTHS_PLACEHOLDER)

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Account update two")
            with Body():
                yield from self.__account_input.compose()
                yield Static("memo key", classes="label")
                yield self.__memo_key_input
                yield Static("json metadata", classes="label")
                yield self.__json_metadata_input
                yield Static("posting json metadata", classes="label")
                yield self.__posting_json_metadata
                yield PlaceTaker()
                yield BigTitle("owner authority")
                yield Static("weight threshold", classes="label")
                yield self.__weight_threshold_owner_input
                yield Static("account auths", classes="label")
                yield self.__account_auths_owner_input
                yield Static("key auths", classes="label")
                yield self.__key_auths_owner_input
                yield PlaceTaker()
                yield BigTitle("active authority")
                yield Static("weight threshold", classes="label")
                yield self.__weight_threshold_active_input
                yield Static("account auths", classes="label")
                yield self.__account_auths_active_input
                yield Static("key auths", classes="label")
                yield self.__key_auths_active_input
                yield PlaceTaker()
                yield BigTitle("posting authority")
                yield Static("weight threshold", classes="label")
                yield self.__weight_threshold_posting_input
                yield Static("account auths", classes="label")
                yield self.__account_auths_posting_input
                yield Static("key auths", classes="label")
                yield self.__key_auths_posting_input

    def _create_operation(self) -> AccountUpdate2Operation:
        owner_authority = self._create_authority_field(
            self.__weight_threshold_owner_input, self.__account_auths_owner_input, self.__key_auths_owner_input
        )

        active_authority = self._create_authority_field(
            self.__weight_threshold_active_input, self.__account_auths_active_input, self.__key_auths_active_input
        )

        posting_authority = self._create_authority_field(
            self.__weight_threshold_posting_input, self.__account_auths_posting_input, self.__key_auths_posting_input
        )

        return AccountUpdate2Operation(
            account=self.__account_input.value,
            memo_key=self.__memo_key_input.value,
            active=active_authority,
            posting=posting_authority,
            owner=owner_authority,
            json_metadata=self.__json_metadata_input.value,
            posting_json_metadata=self.__posting_json_metadata.value,
        )
