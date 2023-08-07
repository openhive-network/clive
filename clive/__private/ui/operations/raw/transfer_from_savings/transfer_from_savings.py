from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.amount_input import AmountInput
from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.memo_input import MemoInput
from clive.__private.ui.widgets.placeholders_constants import ID_PLACEHOLDER
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

        self.__to_input = AccountNameInput(label="to")
        self.__request_id_input = CustomInput(label="request id", value=default_request_id, placeholder=ID_PLACEHOLDER)
        self.__amount_input = AmountInput()
        self.__memo_input = MemoInput(label="memo")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Transfer from savings")
            with ScrollableContainer(), Body():
                yield InputLabel("from")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="from-label")
                yield from self.__to_input.compose()
                yield from self.__request_id_input.compose()
                yield InputLabel("amount")
                yield self.__amount_input
                yield from self.__memo_input.compose()

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
