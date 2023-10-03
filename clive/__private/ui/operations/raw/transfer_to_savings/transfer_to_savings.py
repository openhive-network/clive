from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.asset_amount_input import AssetAmountInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.memo_input import MemoInput
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import TransferToSavingsOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class TransferToSavings(RawOperationBaseScreen):
    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__to_input = AccountNameInput(label="to")
        self.__amount_input = AssetAmountInput()
        self.__memo_input = MemoInput()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Transfer to savings")
            with ScrollableContainer(), Body():
                yield InputLabel("from")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="from-label")
                yield from self.__to_input.compose()
                yield from self.__amount_input.compose()
                yield from self.__memo_input.compose()

    def _create_operation(self) -> TransferToSavingsOperation | None:
        amount = self.__amount_input.value
        if not amount:
            return None

        return TransferToSavingsOperation(
            from_=self.app.world.profile_data.working_account.name,
            to=self.__to_input.value,
            amount=amount,
            memo=self.__memo_input.value,
        )
