from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.amount_input import AmountInput
from clive.__private.ui.widgets.placeholders_constants import MEMO_PLACEHOLDER
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import RecurrentTransferOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Asset


class Body(Grid):
    """All the content of the screen, excluding the title."""


class RecurrentTransfer(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        default_recurrence = str(get_default_from_model(RecurrentTransferOperation, "recurrence", int))
        default_executions = str(get_default_from_model(RecurrentTransferOperation, "executions", int))

        self.__to_input = AccountNameInput(label="to")
        self.__amount_input = AmountInput()
        self.__memo_input = Input(placeholder=MEMO_PLACEHOLDER)
        self.__recurrence_input = Input(default_recurrence, placeholder="e.g.: 26")
        self.__executions_input = Input(default_executions, placeholder="e.g.: 3")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Recurrent transfer")
            with Body():
                yield Static("from", classes="label")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="from-label")
                yield from self.__to_input.compose()
                yield Static("amount", classes="label")
                yield self.__amount_input
                yield Static("memo", classes="label")
                yield self.__memo_input
                yield Static("recurrence", classes="label")
                yield self.__recurrence_input
                yield Static("executions", classes="label")
                yield self.__executions_input

    def _create_operation(self) -> RecurrentTransferOperation[Asset.Hive, Asset.Hbd] | None:
        amount = self.__amount_input.amount
        if not amount:
            return None

        return RecurrentTransferOperation(
            from_=self.app.world.profile_data.name,
            to=self.__to_input.value,
            amount=amount,
            memo=self.__memo_input.value,
            recurrence=int(self.__recurrence_input.value),
            executions=int(self.__executions_input.value),
        )
