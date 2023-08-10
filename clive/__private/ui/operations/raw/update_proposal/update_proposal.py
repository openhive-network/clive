from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.amount_input import AmountInput
from clive.__private.ui.widgets.inputs.id_input import IdInput
from clive.__private.ui.widgets.inputs.permlink_input import PermlinkInput
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import UpdateProposalOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class UpdateProposal(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        self.__proposal_id_input = IdInput(label="proposal id")
        self.__creator_input = AccountNameInput(label="creator")
        self.__daily_pay_input = AmountInput(label="daily pay")
        self.__subject_input = TextInput(label="subject", placeholder="e.g.: New subject")
        self.__permlink_input = PermlinkInput()
        self.__extensions_input = TextInput(label="extensions", placeholder="e.g.: []")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Update proposal")
            with ScrollableContainer(), Body():
                yield from self.__proposal_id_input.compose()
                yield from self.__creator_input.compose()
                yield from self.__daily_pay_input.compose()
                yield from self.__subject_input.compose()
                yield from self.__permlink_input.compose()
                yield from self.__extensions_input.compose()

    def _create_operation(self) -> UpdateProposalOperation[Asset.Hbd]:
        return UpdateProposalOperation(
            proposal_id=self.__proposal_id_input.value,
            creator=self.__creator_input.value,
            daily_pay=Asset.hbd(self.__daily_pay_input.value),
            subject=self.__subject_input.value,
            permlink=self.__permlink_input.value,
            extensions=self.__extensions_input.value,
        )
