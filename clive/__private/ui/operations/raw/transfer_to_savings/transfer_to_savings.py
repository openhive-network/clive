from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.amount_input import AmountInput
from clive.__private.ui.widgets.placeholders_constants import (
    MEMO_PLACEHOLDER,
)
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import TransferToSavingsOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Asset


class Body(Grid):
    """All the content of the screen, excluding the title."""


class TransferToSavings(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        self.__to_input = AccountNameInput(label="to")
        self.__amount_input = AmountInput()
        self.__memo_input = Input(placeholder=MEMO_PLACEHOLDER)

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Transfer to savings")
            with Body():
                yield Static("from", classes="label")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="from-label")
                yield from self.__to_input.compose()
                yield Static("amount", classes="label")
                yield self.__amount_input
                yield Static("memo", classes="label")
                yield self.__memo_input

    def _create_operation(self) -> TransferToSavingsOperation[Asset.Hive, Asset.Hbd] | None:
        amount = self.__amount_input.amount
        if not amount:
            return None

        return TransferToSavingsOperation(
            from_=self.app.world.profile_data.working_account.name,
            to=self.__to_input.value,
            amount=amount,
            memo=self.__memo_input.value,
        )
