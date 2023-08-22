from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.date_input import DateInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.numeric_input import NumericInput
from clive.__private.ui.widgets.inputs.permlink_input import PermlinkInput
from clive.__private.ui.widgets.inputs.text_input import TextInput
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
        self.__start_date_input = DateInput(label="start date")
        self.__end_date_input = DateInput(label="end date")
        self.__daily_pay_input = NumericInput(label="daily hbd pay")
        self.__subject_input = TextInput(label="subject", placeholder="e.g: example subject")
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

    def _create_operation(self) -> CreateProposalOperation[Asset.Hbd] | None:
        daily_pay_value = self.__daily_pay_input.value
        if not daily_pay_value:
            return None

        return CreateProposalOperation(
            creator=self.app.world.profile_data.name,
            receiver=self.__receiver_input.value,
            start_date=self.__start_date_input.value,
            end_date=self.__end_date_input.value,
            daily_pay=Asset.hbd(daily_pay_value),
            subject=self.__subject_input.value,
            permlink=self.__permlink_input.value,
        )
