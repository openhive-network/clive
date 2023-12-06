from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.placeholders_constants import ACCOUNT_NAME2_PLACEHOLDER
from schemas.operations import ChangeRecoveryAccountOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class ChangeRecoveryAccount(RawOperationBaseScreen):
    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__account_to_recover_input = AccountNameInput(label="account to recover")
        self.__new_recovery_account_input = AccountNameInput(
            label="new recovery account", placeholder=ACCOUNT_NAME2_PLACEHOLDER
        )

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Change recovery account")
        with ScrollableContainer(), Body():
            yield from self.__account_to_recover_input.compose()
            yield from self.__new_recovery_account_input.compose()

    def _create_operation(self) -> ChangeRecoveryAccountOperation:
        return ChangeRecoveryAccountOperation(
            account_to_recover=self.__account_to_recover_input.value,
            new_recovery_account=self.__new_recovery_account_input.value,
            extensions=[],
        )
