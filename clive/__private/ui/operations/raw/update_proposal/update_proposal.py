from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.permlink_input import PermlinkInput
from clive.__private.ui.widgets.placeholders_constants import (
    ASSET_AMOUNT_PLACEHOLDER,
    ID_PLACEHOLDER,
)
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

        self.__proposal_id_input = Input(placeholder=ID_PLACEHOLDER)
        self.__creator_input = AccountNameInput(label="creator")
        self.__daily_pay_input = Input(placeholder=ASSET_AMOUNT_PLACEHOLDER)
        self.__subject_input = Input(placeholder="e.g.: New subject")
        self.__permlink_input = PermlinkInput(label="permlink")
        self.__extensions_input = Input(placeholder="e.g.: []")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Update proposal")
            with Body():
                yield Static("proposal id", classes="label")
                yield self.__proposal_id_input
                yield from self.__creator_input.compose()
                yield Static("daily pay", classes="label")
                yield self.__daily_pay_input
                yield Static("subject", classes="label")
                yield self.__subject_input
                yield from self.__permlink_input.compose()
                yield Static("extensions", classes="label")
                yield self.__extensions_input

    def _create_operation(self) -> UpdateProposalOperation[Asset.Hbd]:
        return UpdateProposalOperation(
            proposal_id=int(self.__proposal_id_input.value),
            creator=self.__creator_input.value,
            daily_pay=Asset.hbd(self.__daily_pay_input.value),
            subject=self.__subject_input.value,
            permlink=self.__permlink_input.value,
            extensions=self.__extensions_input.value,
        )
