from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer
from textual.widgets import Static

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import RemoveProposalOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class RemoveProposal(RawOperationBaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self) -> None:
        super().__init__()

        self.__proposal_ids_input = TextInput(label="proposal ids", placeholder="e.g.: 10,11,12")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Remove proposal")
            with ScrollableContainer(), Body():
                yield InputLabel("proposal_owner")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="owner-label")
                yield PlaceTaker()
                yield from self.__proposal_ids_input.compose()

    def _create_operation(self) -> RemoveProposalOperation:
        split_ids: list[str] = self.__proposal_ids_input.value.split(",")
        split_ids = [x.strip(" ") for x in split_ids]
        proposal_ids_list: list[int] = [int(v) for v in split_ids]

        return RemoveProposalOperation(proposal_owner=self.app.world.profile_data.name, proposal_ids=proposal_ids_list)
