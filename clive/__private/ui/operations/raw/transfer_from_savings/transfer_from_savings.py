from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.asset_amount_input import AssetAmountInput
from clive.__private.ui.widgets.inputs.id_input import IdInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.memo_input import MemoInput
from schemas.operations import TransferFromSavingsOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class TransferFromSavings(RawOperationBaseScreen):
    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self) -> None:
        super().__init__()

        default_request_id = get_default_from_model(TransferFromSavingsOperation, "request_id", int)

        self.__to_input = AccountNameInput(label="to")
        self.__request_id_input = IdInput(label="request id", value=default_request_id)
        self.__amount_input = AssetAmountInput()
        self.__memo_input = MemoInput()

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Transfer from savings")
        with ScrollableContainer(), Body():
            yield InputLabel("from")
            yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="from-label")
            yield from self.__to_input.compose()
            yield from self.__request_id_input.compose()
            yield from self.__amount_input.compose()
            yield from self.__memo_input.compose()

    def _create_operation(self) -> TransferFromSavingsOperation | None:
        amount = self.__amount_input.value
        request_id = self.__request_id_input.value

        if not amount or not request_id:
            return None

        return TransferFromSavingsOperation(
            from_=self.app.world.profile_data.working_account.name,
            to=self.__to_input.value,
            request_id=request_id,
            amount=amount,
            memo=self.__memo_input.value,
        )
