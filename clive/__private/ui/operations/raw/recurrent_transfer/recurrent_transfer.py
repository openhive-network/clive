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
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.inputs.memo_input import MemoInput
from schemas.operations import RecurrentTransferOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class RecurrentTransfer(RawOperationBaseScreen):
    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self) -> None:
        super().__init__()

        default_recurrence = get_default_from_model(RecurrentTransferOperation, "recurrence", int)
        default_executions = get_default_from_model(RecurrentTransferOperation, "executions", int)

        self.__to_input = AccountNameInput(label="to")
        self.__amount_input = AssetAmountInput()
        self.__memo_input = MemoInput()
        self.__recurrence_input = IntegerInput(label="recurrence", value=default_recurrence, placeholder="e.g.: 26")
        self.__executions_input = IntegerInput(label="executions", value=default_executions, placeholder="e.g.: 3")

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Recurrent transfer")
        with ScrollableContainer(), Body():
            yield InputLabel("from")
            yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="from-label")
            yield from self.__to_input.compose()
            yield from self.__amount_input.compose()
            yield from self.__memo_input.compose()
            yield from self.__recurrence_input.compose()
            yield from self.__executions_input.compose()

    def _create_operation(self) -> RecurrentTransferOperation | None:
        amount = self.__amount_input.value
        recurrence = self.__recurrence_input.value
        executions = self.__executions_input.value
        if not amount or not recurrence or not executions:
            return None

        return RecurrentTransferOperation(
            from_=self.app.world.profile_data.working_account.name,
            to=self.__to_input.value,
            amount=amount,
            memo=self.__memo_input.value,
            recurrence=recurrence,
            executions=executions,
            extensions=[],
        )
