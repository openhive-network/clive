from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.amount_input import AmountInput
from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.permlink_input import PermlinkInput
from clive.__private.ui.widgets.placeholders_constants import (
    DATE_PLACEHOLDER,
)
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import CreateProposalOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class CreateProposal(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        self.__receiver_input = AccountNameInput(label="receiver")
        self.__start_date_input = CustomInput(label="start date", placeholder=DATE_PLACEHOLDER)
        self.__end_date_input = CustomInput(label="end date", placeholder=DATE_PLACEHOLDER)
        self.__daily_pay_input = AmountInput(label="daily pay")
        self.__subject_input = CustomInput(label="subject", placeholder="e.g: example subject")
        self.__permlink_input = PermlinkInput()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Create proposal")
            with ScrollableContainer(), Body():
                yield InputLabel("creator")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="creator-label")
                yield from self.__receiver_input.compose()
                yield from self.__start_date_input.compose()
                yield from self.__end_date_input.compose()
                yield from self.__daily_pay_input.compose()
                yield from self.__subject_input.compose()
                yield from self.__permlink_input.compose()

    def _create_operation(self) -> CreateProposalOperation[Asset.Hbd]:
        return CreateProposalOperation(
            creator=self.app.world.profile_data.name,
            receiver=self.__receiver_input.value,
            start_date=self.__start_date_input.value,
            end_date=self.__end_date_input.value,
            daily_pay=Asset.hbd(self.__daily_pay_input.value),
            subject=self.__subject_input.value,
            permlink=self.__permlink_input.value,
        )
