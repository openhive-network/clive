from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.fee_input import FeeInput
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import ClaimAccountOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class ClaimAccount(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        self.__creator_input = AccountNameInput(label="creator")
        self.__fee_input = FeeInput()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Claim account")
            with ScrollableContainer(), Body():
                yield from self.__creator_input.compose()
                yield from self.__fee_input.compose()

    def _create_operation(self) -> ClaimAccountOperation | None:
        fee = self.__fee_input.value
        if not fee:
            return None

        return ClaimAccountOperation(creator=self.__creator_input.value, fee=Asset.hive(fee))
