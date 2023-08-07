from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.amount_input import AmountInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.memo_input import MemoInput
from clive.__private.ui.widgets.known_account import KnownAccount
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

        self.__to_input = AccountNameInput(label="to")
        self.__memo_input = MemoInput(label="memo")

        self.__amount_input = AmountInput()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Transfer to account")
            with ScrollableContainer(), Body():
                to_label, to_input = self.__to_input.compose()

                yield InputLabel("from")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="from-label")
                yield to_label
                yield to_input
                yield KnownAccount(to_input)
                yield InputLabel("amount")
                yield self.__amount_input
                yield from self.__memo_input.compose()

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
