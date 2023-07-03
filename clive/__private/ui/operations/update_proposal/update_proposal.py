from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.operation_base import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import UpdateProposalOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from schemas.__private.hive_fields_basic_schemas import AssetHbdHF26


class Body(Grid):
    """All the content of the screen, excluding the title"""


class UpdateProposal(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        self.__proposal_id_input = Input(placeholder="e.g.: 1000")
        self.__creator_input = Input(placeholder="e.g.: alice")
        self.__daily_pay_input = Input(placeholder="e.g.: 2.000")
        self.__subject_input = Input(placeholder="e.g.: pizza day")
        self.__permlink_input = Input(placeholder="e.g.: a-post-by-alice")
        self.__extensions_input = Input(placeholder="e.g.: []")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Update proposal")
            with Body():
                yield Static("proposal id", classes="label")
                yield self.__proposal_id_input
                yield Static("creator", classes="label")
                yield self.__creator_input
                yield Static("daily pay", classes="label")
                yield self.__daily_pay_input
                yield Static("subject", classes="label")
                yield self.__subject_input
                yield Static("permlink", classes="label")
                yield self.__permlink_input
                yield Static("extensions", classes="label")
                yield self.__extensions_input

    def _create_operation(self) -> UpdateProposalOperation[AssetHbdHF26]:
        return UpdateProposalOperation(
            proposal_id=int(self.__proposal_id_input.value),
            creator=self.__creator_input.value,
            daily_pay=Asset.hbd(float(self.__daily_pay_input.value)),
            subject=self.__subject_input.value,
            permlink=self.__permlink_input.value,
            extensions=self.__extensions_input.value,  # Notice: this operation is not working, cause it was mistake in schemas, need to update schemas
        )
