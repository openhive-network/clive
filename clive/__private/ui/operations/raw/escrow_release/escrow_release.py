from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.id_input import IdInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.numeric_input import NumericInput
from clive.__private.ui.widgets.placeholders_constants import (
    ACCOUNT_NAME2_PLACEHOLDER,
)
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import EscrowReleaseOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class EscrowRelease(RawOperationBaseScreen):
    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self) -> None:
        super().__init__()

        default_escrow_id = get_default_from_model(EscrowReleaseOperation, "escrow_id", int)

        self.__to_input = AccountNameInput(label="to")
        self.__agent_input = AccountNameInput(label="agent", placeholder=ACCOUNT_NAME2_PLACEHOLDER)
        self.__who_input = AccountNameInput(label="who", placeholder=ACCOUNT_NAME2_PLACEHOLDER)
        self.__receiver_input = AccountNameInput(label="receiver")
        self.__escrow_id_input = IdInput(label="escrow id", value=default_escrow_id)
        self.__hbd_amount_input = NumericInput(
            label="hbd amount", placeholder="Notice: if don't want to use, leave 0.000 here", value=0.000
        )
        self.__hive_amount_input = NumericInput(
            label="hive amount", placeholder="Notice: if don't want to use, leave 0.000 here", value=0.000
        )

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Escrow release")
            with ScrollableContainer(), Body():
                yield InputLabel("from")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="from-label")
                yield from self.__to_input.compose()
                yield from self.__agent_input.compose()
                yield from self.__who_input.compose()
                yield from self.__receiver_input.compose()
                yield from self.__escrow_id_input.compose()
                yield from self.__hbd_amount_input.compose()
                yield from self.__hive_amount_input.compose()

    def _create_operation(self) -> EscrowReleaseOperation | None:
        hbd_amount = self.__hbd_amount_input.value
        hive_amount = self.__hive_amount_input.value
        escrow_id = self.__escrow_id_input.value

        if not escrow_id or not hive_amount or not hbd_amount:
            return None

        return EscrowReleaseOperation(
            from_=self.app.world.profile_data.name,
            to=self.__to_input.value,
            agent=self.__agent_input.value,
            escrow_id=escrow_id,
            hbd_amount=Asset.hbd(hbd_amount),
            hive_amount=Asset.hive(hive_amount),
            receiver=self.__receiver_input.value,
            who=self.__who_input.value,
        )
