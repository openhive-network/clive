from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Checkbox, Static

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import UpdateProposalVotesOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class UpdateProposalVotes(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        default_approve = get_default_from_model(UpdateProposalVotesOperation, "approve", bool)

        self.__proposal_ids = CustomInput(label="proposal ids", placeholder="e.g.: 10,11,12")
        self.__approve_input = Checkbox("approve", value=default_approve)

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Update proposal votes")
            with Body():
                yield Static("voter", classes="label")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="voter-label")
                yield PlaceTaker()
                yield from self.__proposal_ids.compose()
                yield self.__approve_input

    def _create_operation(self) -> UpdateProposalVotesOperation:
        split_ids: list[str] = self.__proposal_ids.value.split(",")
        split_ids = [x.strip(" ") for x in split_ids]
        proposal_ids_list: list[int] = [int(v) for v in split_ids]

        return UpdateProposalVotesOperation(
            voter=self.app.world.profile_data.working_account.name,
            proposal_ids=proposal_ids_list,
            approve=self.__approve_input.value,
        )
