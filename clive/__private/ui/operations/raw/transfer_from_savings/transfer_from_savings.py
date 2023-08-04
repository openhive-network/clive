from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.amount_input import AmountInput
from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.inputs.memo_input import MemoInput
from clive.__private.ui.widgets.placeholders_constants import ACCOUNT_NAME_PLACEHOLDER, ID_PLACEHOLDER
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import TransferFromSavingsOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Asset


class Body(Grid):
    """All the content of the screen, excluding the title."""


class TransferFromSavings(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        default_request_id = str(get_default_from_model(TransferFromSavingsOperation, "request_id", int))

        self.__to_input = Input(placeholder=ACCOUNT_NAME_PLACEHOLDER)
        self.__request_id_input = CustomInput(
            label="request id", default_value=default_request_id, placeholder=ID_PLACEHOLDER
        )
        self.__amount_input = AmountInput()
        self.__memo_input = MemoInput()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Transfer from savings")
            with Body():
                yield Static("from", classes="label")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="from-label")
                yield Static("to", classes="label")
                yield self.__to_input
                yield Static("request id", classes="label")
                yield self.__request_id_input
                yield Static("amount", classes="label")
                yield self.__amount_input
                yield Static("memo", classes="label")
                yield self.__memo_input

    def _create_operation(self) -> TransferFromSavingsOperation[Asset.Hive, Asset.Hbd] | None:
        amount = self.__amount_input.amount
        if not amount:
            return None

        return TransferFromSavingsOperation(
            from_=self.app.world.profile_data.working_account.name,
            to=self.__to_input.value,
            request_id=int(self.__request_id_input.value),
            amount=amount,
            memo=self.__memo_input.value,
        )
