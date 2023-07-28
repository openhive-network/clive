from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.known_account import KnownAccount
from clive.__private.ui.widgets.inputs.amount_input import AmountInput
from clive.__private.ui.widgets.placeholders_constants import (
    ACCOUNT_NAME_PLACEHOLDER,
    MEMO_PLACEHOLDER,
)
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from clive.models.asset import AssetAmountT
from schemas.operations import TransferOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


LiquidAssetCallableT = Callable[[AssetAmountT], Asset.LiquidT]


class Body(Grid):
    """All the content of the screen, excluding the title."""


class TransferToAccount(OperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        self.__to_input = Input(placeholder=ACCOUNT_NAME_PLACEHOLDER)
        self.__memo_input = Input(placeholder=MEMO_PLACEHOLDER)

        self.__amount_input = AmountInput()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Transfer to account")
            with Body():
                yield Static("from", classes="label")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="from-label")
                yield Static("to", classes="label")
                yield self.__to_input
                yield KnownAccount(self.__to_input)
                yield Static("amount", classes="label")
                yield self.__amount_input
                yield Static("memo", classes="label")
                yield self.__memo_input

    def _create_operation(self) -> TransferOperation[Asset.Hive, Asset.Hbd] | None:
        amount = self.__amount_input.amount
        if not amount:
            return None

        return TransferOperation(
            from_=self.app.world.profile_data.working_account.name,
            to=self.__to_input.value,
            amount=amount,
            memo=self.__memo_input.value,
        )
