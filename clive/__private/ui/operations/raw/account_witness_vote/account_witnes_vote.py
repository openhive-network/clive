from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Checkbox, Input, Static

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.placeholders_constants import WITNESS_PLACEHOLDER
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import AccountWitnessVoteOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class AccountWitnessVote(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        default_approve = get_default_from_model(AccountWitnessVoteOperation, "approve", bool)

        self.__witness_input = Input(placeholder=WITNESS_PLACEHOLDER)
        self.__approve_input = Checkbox("approve", value=default_approve)

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Account witness vote")
            with Body():
                yield Static("account", classes="label")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="account-label")
                yield PlaceTaker()
                yield Static("witness", classes="label")
                yield self.__witness_input
                yield self.__approve_input

    def _create_operation(self) -> AccountWitnessVoteOperation:
        return AccountWitnessVoteOperation(
            account=self.app.world.profile_data.working_account.name,
            witness=self.__witness_input.value,
            approve=self.__approve_input.value,
        )
