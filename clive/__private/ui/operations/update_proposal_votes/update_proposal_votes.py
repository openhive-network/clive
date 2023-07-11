from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.operation_base import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import UpdateProposalVotesOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class UpdateProposalVotes(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        default_approve = str(get_default_from_model(UpdateProposalVotesOperation, "approve"))

        self.__proposal_ids = Input(placeholder="e.g.: 10,11,12")
        self.__approve_input = Input(default_approve, placeholder="e.g.: True")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Update proposal votes")
            with Body():
                yield Static("voter", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="voter-label")
                yield PlaceTaker()
                yield Static("proposal ids", classes="label")
                yield self.__proposal_ids
                yield Static("approve", classes="label")
                yield self.__approve_input

    def _create_operation(self) -> UpdateProposalVotesOperation:
        split_ids: list[str] = self.__proposal_ids.value.split(",")
        split_ids = [x.strip(" ") for x in split_ids]
        proposal_ids_list: list[int] = [int(v) for v in split_ids]

        return UpdateProposalVotesOperation(
            voter=str(self.app.world.profile_data.working_account.name),
            proposal_ids=proposal_ids_list,
            approve=bool(self.__approve_input.value),
        )
