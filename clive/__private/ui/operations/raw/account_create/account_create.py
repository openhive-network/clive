from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_auths_input import AccountAuthsInput
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.key_auths_input import KeyAuthsInput
from clive.__private.ui.widgets.placeholders_constants import (
    ASSET_AMOUNT_PLACEHOLDER,
    JSON_DATA_PLACEHOLDER,
    KEY_PLACEHOLDER,
    WEIGHT_THRESHOLD_PLACEHOLDER,
)
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import AccountCreateOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of owner authority part."""


class AccountCreate(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        self.__new_account_name_input = AccountNameInput(label="new account name")
        self.__fee_input = Input(placeholder=ASSET_AMOUNT_PLACEHOLDER)

        self.__weight_threshold_owner_input = Input(placeholder=WEIGHT_THRESHOLD_PLACEHOLDER)
        self.__account_auths_owner_input = AccountAuthsInput(label="account auths")
        self.__key_auths_owner_input = KeyAuthsInput(label="key auths")

        self.__weight_threshold_active_input = Input(placeholder=WEIGHT_THRESHOLD_PLACEHOLDER)
        self.__account_auths_active_input = AccountAuthsInput(label="account auths")
        self.__key_auths_active_input = KeyAuthsInput(label="key auths")

        self.__weight_threshold_posting_input = Input(placeholder=WEIGHT_THRESHOLD_PLACEHOLDER)
        self.__account_auths_posting_input = AccountAuthsInput(label="account auths")
        self.__key_auths_posting_input = KeyAuthsInput(label="key auths")

        self.__memo_key_input = Input(placeholder=KEY_PLACEHOLDER)
        self.__json_metadata_input = Input(placeholder=JSON_DATA_PLACEHOLDER)

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Account create")
            with Body():
                yield Static("creator", classes="label")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="creator-label")
                yield from self.__new_account_name_input.compose()
                yield Static("fee", classes="label")
                yield self.__fee_input
                yield Static("memo key", classes="label")
                yield self.__memo_key_input
                yield Static("json metadata", classes="label")
                yield self.__json_metadata_input
                yield PlaceTaker()
                yield BigTitle("owner authority")
                yield Static("weight threshold", classes="label")
                yield self.__weight_threshold_owner_input
                yield from self.__account_auths_owner_input.compose()
                yield from self.__key_auths_owner_input.compose()
                yield PlaceTaker()
                yield BigTitle("active authority")
                yield Static("weight threshold", classes="label")
                yield self.__weight_threshold_active_input
                yield from self.__account_auths_active_input.compose()
                yield from self.__key_auths_active_input.compose()
                yield PlaceTaker()
                yield BigTitle("posting authority")
                yield Static("weight threshold", classes="label")
                yield self.__weight_threshold_posting_input
                yield from self.__account_auths_posting_input.compose()
                yield from self.__key_auths_posting_input.compose()

    def _create_operation(self) -> AccountCreateOperation[Asset.Hive]:
        owner_authority = self._create_authority_field(
            self.__weight_threshold_owner_input, self.__account_auths_owner_input, self.__key_auths_owner_input
        )

        active_authority = self._create_authority_field(
            self.__weight_threshold_active_input, self.__account_auths_active_input, self.__key_auths_active_input
        )

        posting_authority = self._create_authority_field(
            self.__weight_threshold_posting_input, self.__account_auths_posting_input, self.__key_auths_posting_input
        )

        return AccountCreateOperation(
            creator=self.app.world.profile_data.name,
            fee=Asset.hive(self.__fee_input.value),
            new_account_name=self.__new_account_name_input.value,
            owner=owner_authority,
            active=active_authority,
            posting=posting_authority,
            memo_key=self.__memo_key_input.value,
            json_metadata=self.__json_metadata_input.value,
        )
