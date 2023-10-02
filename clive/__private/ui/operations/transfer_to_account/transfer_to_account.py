from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer
from textual.widgets import Static

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen, OperationMethods
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.asset_amount_input import AssetAmountInput
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


class TransferToAccount(OperationBaseScreen, OperationMethods):
    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self) -> None:
        super().__init__()

        self.__to_input = AccountNameInput(label="to")
        self.__memo_input = MemoInput()

        self.__amount_input = AssetAmountInput()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Transfer to account")
            with ScrollableContainer(), Body():
                to_label, to_input = self.__to_input.compose()

                yield InputLabel("from")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="from-label")
                yield Static()
                yield to_label
                yield to_input
                yield KnownAccount(to_input)  # type: ignore[arg-type]
                yield from self.__amount_input.compose()
                yield Static()
                yield from self.__memo_input.compose()

    def _create_operation(self) -> TransferOperation | None:
        amount = self.__amount_input.value
        if not amount:
            return None

        return TransferOperation(
            from_=self.app.world.profile_data.working_account.name,
            to=self.__to_input.value,
            amount=amount,
            memo=self.__memo_input.value,
        )
