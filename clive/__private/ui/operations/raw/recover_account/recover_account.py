from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer
from textual.widgets import Static

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.inputs.account_auths_input import AccountAuthsInput
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.key_auths_input import KeyAuthsInput
from clive.__private.ui.widgets.inputs.weight_threshold_input import WeightThresholdInput
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import RecoverAccountOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of new owner authority."""


class RecoverAccount(RawOperationBaseScreen):
    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__account_to_recover_input = AccountNameInput()
        self.__weight_threshold_new_input = WeightThresholdInput()
        self.__account_auths_new_input = AccountAuthsInput()
        self.__key_auths_new_input = KeyAuthsInput()
        self.__weight_threshold_recent_input = WeightThresholdInput()
        self.__account_auths_recent_input = AccountAuthsInput()
        self.__key_auths_recent_input = KeyAuthsInput()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Recover account")
            with ScrollableContainer(), Body():
                yield from self.__account_to_recover_input.compose()
                yield PlaceTaker()
                yield BigTitle("New owner authority")
                yield from self.__weight_threshold_new_input.compose()
                yield from self.__account_auths_new_input.compose()
                yield from self.__key_auths_new_input.compose()
                yield PlaceTaker()
                yield BigTitle("Recent owner authority")
                yield from self.__weight_threshold_recent_input.compose()
                yield from self.__account_auths_recent_input.compose()
                yield from self.__key_auths_recent_input.compose()

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
