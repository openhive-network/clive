from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Static

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.placeholders_constants import (
    ACCOUNT_NAME2_PLACEHOLDER,
    ID_PLACEHOLDER,
)
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import EscrowDisputeOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class EscrowDispute(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        default_escrow_id = str(get_default_from_model(EscrowDisputeOperation, "escrow_id", int))

        self.__to_input = AccountNameInput(label="to")
        self.__agent_input = AccountNameInput(label="agent", placeholder=ACCOUNT_NAME2_PLACEHOLDER)
        self.__who_input = AccountNameInput(label="who", placeholder=ACCOUNT_NAME2_PLACEHOLDER)
        self.__escrow_id_input = CustomInput(
            label="escrow id", default_value=default_escrow_id, placeholder=ID_PLACEHOLDER
        )

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Escrow dispute")
            with Body():
                yield Static("from", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="from-label")
                yield PlaceTaker()
                yield from self.__to_input.compose()
                yield from self.__agent_input.compose()
                yield from self.__who_input.compose()
                yield from self.__escrow_id_input.compose()

    def _create_operation(self) -> EscrowDisputeOperation:
        return EscrowDisputeOperation(
            from_=str(self.app.world.profile_data.name),
            to=self.__to_input.value,
            agent=self.__agent_input.value,
            escrow_id=int(self.__escrow_id_input.value),
            who=self.__who_input.value,
        )
