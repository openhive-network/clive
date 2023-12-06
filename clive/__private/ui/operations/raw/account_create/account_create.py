from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer
from textual.widgets import Static

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_auths_input import AccountAuthsInput
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.fee_input import FeeInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.json_data_input import JsonDataInput
from clive.__private.ui.widgets.inputs.key_auths_input import KeyAuthsInput
from clive.__private.ui.widgets.inputs.memo_key_input import MemoKeyInput
from clive.__private.ui.widgets.inputs.weight_threshold_input import WeightThresholdInput
from clive.models import Asset
from schemas.operations import AccountCreateOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of owner authority part."""


class AccountCreate(RawOperationBaseScreen):
    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__new_account_name_input = AccountNameInput(label="new account name")
        self.__fee_input = FeeInput()

        self.__weight_threshold_owner_input = WeightThresholdInput()
        self.__account_auths_owner_input = AccountAuthsInput()
        self.__key_auths_owner_input = KeyAuthsInput()

        self.__weight_threshold_active_input = WeightThresholdInput()
        self.__account_auths_active_input = AccountAuthsInput()
        self.__key_auths_active_input = KeyAuthsInput()

        self.__weight_threshold_posting_input = WeightThresholdInput()
        self.__account_auths_posting_input = AccountAuthsInput()
        self.__key_auths_posting_input = KeyAuthsInput()

        self.__memo_key_input = MemoKeyInput()
        self.__json_metadata_input = JsonDataInput()

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Account create")
        with ScrollableContainer(), Body():
            yield InputLabel("creator")
            yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="creator-label")
            yield from self.__new_account_name_input.compose()
            yield from self.__fee_input.compose()
            yield from self.__memo_key_input.compose()
            yield from self.__json_metadata_input.compose()
            yield PlaceTaker()
            yield BigTitle("owner authority")
            yield from self.__weight_threshold_owner_input.compose()
            yield from self.__account_auths_owner_input.compose()
            yield from self.__key_auths_owner_input.compose()
            yield PlaceTaker()
            yield BigTitle("active authority")
            yield from self.__weight_threshold_active_input.compose()
            yield from self.__account_auths_active_input.compose()
            yield from self.__key_auths_active_input.compose()
            yield PlaceTaker()
            yield BigTitle("posting authority")
            yield from self.__weight_threshold_posting_input.compose()
            yield from self.__account_auths_posting_input.compose()
            yield from self.__key_auths_posting_input.compose()

    def _create_operation(self) -> AccountCreateOperation | None:
        fee = self.__fee_input.value
        if not fee:
            return None

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
            creator=self.app.world.profile_data.working_account.name,
            fee=Asset.hive(fee),
            new_account_name=self.__new_account_name_input.value,
            owner=owner_authority,
            active=active_authority,
            posting=posting_authority,
            memo_key=self.__memo_key_input.value,
            json_metadata=self.__json_metadata_input.value,
        )
