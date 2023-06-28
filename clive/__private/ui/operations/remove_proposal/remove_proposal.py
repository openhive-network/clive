from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.cart_based_screen.cart_based_screen import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import RemoveProposalOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class RemoveProposal(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        self.__proposal_ids_input = Input(placeholder="e.g.: 10,11,12")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Remove proposal")
            with Body():
                yield Static("proposal_owner", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="owner-label")
                yield PlaceTaker()
                yield Static("proposal ids", classes="label")
                yield self.__proposal_ids_input

    def _create_operation(self) -> Operation | None:
        split_ids: list[str] = self.__proposal_ids_input.value.split(",")
        split_ids = [x.strip(" ") for x in split_ids]
        proposal_ids_list: list[int] = [int(v) for v in split_ids]

        return RemoveProposalOperation(
            proposal_owner=str(self.app.world.profile_data.name), proposal_ids=proposal_ids_list
        )
