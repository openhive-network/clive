from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.asset_amount_input import AssetAmountInput
from clive.__private.ui.widgets.inputs.date_input import DateInput
from clive.__private.ui.widgets.inputs.id_input import IdInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.json_data_input import JsonDataInput
from clive.__private.ui.widgets.inputs.numeric_input import NumericInput
from clive.__private.ui.widgets.placeholders_constants import (
    ACCOUNT_NAME2_PLACEHOLDER,
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

        default_escrow_id = get_default_from_model(EscrowTransferOperation, "escrow_id", int)

        self.__to_input = AccountNameInput(label="to")
        self.__agent_input = AccountNameInput(label="agent", placeholder=ACCOUNT_NAME2_PLACEHOLDER)
        self.__escrow_id_input = IdInput(label="escrow id", value=default_escrow_id)
        self.__hbd_amount_input = NumericInput(
            label="hbd amount", placeholder="Notice: if don't want to use, leave 0.000 here", value=0.000
        )
        self.__hive_amount_input = NumericInput(
            label="hive amount", placeholder="Notice: if don't want to use, leave 0.000 here", value=0.000
        )
        self.__fee_input = AssetAmountInput()
        self.__ratification_deadline_input = DateInput(label="ratification deadline")
        self.__escrow_expiration_input = DateInput(label="escrow expiration")
        self.__json_meta_input = JsonDataInput(label="json meta")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Escrow transfer")
            with ScrollableContainer(), Body():
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
                yield from self.__fee_input.compose()

    def _create_operation(self) -> EscrowTransferOperation[Asset.Hive, Asset.Hbd] | None:
        fee = self.__fee_input.value
        hbd_amount = self.__hbd_amount_input.value
        hive_amount = self.__hive_amount_input.value
        if not fee or not hbd_amount or not hive_amount:
            return None

        return EscrowTransferOperation(
            from_=self.app.world.profile_data.name,
            to=self.__to_input.value,
            agent=self.__agent_input.value,
            escrow_id=self.__escrow_id_input.value,
            hbd_amount=Asset.hbd(hbd_amount),
            hive_amount=Asset.hive(hive_amount),
            ratification_deadline=self.__ratification_deadline_input.value,
            escrow_expiration=self.__ratification_deadline_input.value,
            json_meta=self.__json_meta_input.value,
            fee=fee,
        )
