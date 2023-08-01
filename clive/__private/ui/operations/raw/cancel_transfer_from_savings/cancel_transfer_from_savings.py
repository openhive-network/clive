from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.id_input import IdInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import CancelTransferFromSavingsOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class CancelTransferFromSavings(RawOperationBaseScreen):
    def __init__(
        self,
        request_id: str | None = None,
        to: str | None = None,
        amount: str | None = None,
        memo: str | None = None,
    ) -> None:
        self.__request_id = request_id

        self.__to_account = to
        self.__amount = amount
        self.__memo = memo
        super().__init__()

        if self.__request_id is None:
            default_request_id = str(get_default_from_model(CancelTransferFromSavingsOperation, "request_id", int))
            self.__request_id_input = IdInput(label="request id", value=default_request_id)
        else:
            self.__request_id_input = IdInput(label="request id", value=self.__request_id)

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Cancel transfer from savings")
            with ScrollableContainer(), Body():
                yield InputLabel("from")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, classes="parameters-label")
                if self.__request_id is None:
                    yield from self.__request_id_input.compose()
                else:
                    yield InputLabel("request id")
                    yield EllipsedStatic(self.__request_id, classes="parameters-label")
                    yield InputLabel("to")
                    yield EllipsedStatic(self.__to_account, classes="parameters-label")  # type: ignore
                    yield InputLabel("amount", classes="label")
                    yield EllipsedStatic(self.__amount, classes="parameters-label")  # type: ignore
                    yield InputLabel("memo", classes="label")
                    yield EllipsedStatic(self.__memo, classes="parameters-label")  # type: ignore

    def _create_operation(self) -> CancelTransferFromSavingsOperation | None:
        request_id = self.__request_id_input.value
        if not request_id:
            return None

        return CancelTransferFromSavingsOperation(
            from_=self.app.world.profile_data.working_account.name,
            request_id=request_id,
        )
