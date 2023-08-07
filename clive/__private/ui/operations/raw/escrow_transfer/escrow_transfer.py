from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.amount_input import AmountInput
from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.json_data_input import JsonDataInput
from clive.__private.ui.widgets.placeholders_constants import (
    ACCOUNT_NAME2_PLACEHOLDER,
    DATE_PLACEHOLDER,
    ID_PLACEHOLDER,
)
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import EscrowTransferOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class EscrowTransfer(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        default_escrow_id = str(get_default_from_model(EscrowTransferOperation, "escrow_id", int))

        self.__to_input = AccountNameInput(label="to")
        self.__agent_input = AccountNameInput(label="agent", placeholder=ACCOUNT_NAME2_PLACEHOLDER)
        self.__escrow_id_input = CustomInput(
            label="escrow id", default_value=default_escrow_id, placeholder=ID_PLACEHOLDER
        )
        self.__hbd_amount_input = CustomInput(
            label="hbd amount", placeholder="Notice: if don't want to use, leave 0.000 here", default_value="0.000"
        )
        self.__hive_amount_input = CustomInput(
            label="hive amount", placeholder="Notice: if don't want to use, leave 0.000 here", default_value="0.000"
        )
        self.__fee_input = AmountInput()
        self.__ratification_deadline_input = CustomInput(label="ratification deadline", placeholder=DATE_PLACEHOLDER)
        self.__escrow_expiration_input = CustomInput(label="escrow expiration", placeholder=DATE_PLACEHOLDER)
        self.__json_meta_input = JsonDataInput(label="json meta")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Escrow transfer")
            with Body():
                yield InputLabel("from")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="from-label")
                yield from self.__to_input.compose()
                yield from self.__agent_input.compose()
                yield from self.__escrow_id_input.compose()
                yield from self.__hbd_amount_input.compose()
                yield from self.__hive_amount_input.compose()
                yield from self.__ratification_deadline_input.compose()
                yield from self.__escrow_expiration_input.compose()
                yield from self.__json_meta_input.compose()
                yield self.__fee_input

    def _create_operation(self) -> EscrowTransferOperation[Asset.Hive, Asset.Hbd] | None:
        fee = self.__fee_input.amount
        if not fee:
            return None

        return EscrowTransferOperation(
            from_=self.app.world.profile_data.name,
            to=self.__to_input.value,
            agent=self.__agent_input.value,
            escrow_id=int(self.__escrow_id_input.value),
            hbd_amount=Asset.hbd(self.__hbd_amount_input.value),
            hive_amount=Asset.hive(self.__hive_amount_input.value),
            ratification_deadline=self.__ratification_deadline_input.value,
            escrow_expiration=self.__ratification_deadline_input.value,
            json_meta=self.__json_meta_input.value,
            fee=fee,
        )
