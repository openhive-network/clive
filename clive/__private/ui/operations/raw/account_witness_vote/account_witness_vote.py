from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer
from textual.widgets import Checkbox

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.witness_input import WitnessInput
from schemas.operations import AccountWitnessVoteOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class AccountWitnessVote(RawOperationBaseScreen):
    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self) -> None:
        super().__init__()

        default_approve = get_default_from_model(AccountWitnessVoteOperation, "approve", bool)

        self.__witness_input = WitnessInput()
        self.__approve_input = Checkbox("approve", value=default_approve)

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Account witness vote")
        with ScrollableContainer(), Body():
            yield InputLabel("account")
            yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="account-label")
            yield from self.__witness_input.compose()
            yield self.__approve_input

    def _create_operation(self) -> AccountWitnessVoteOperation:
        return AccountWitnessVoteOperation(
            account=self.app.world.profile_data.working_account.name,
            witness=self.__witness_input.value,
            approve=self.__approve_input.value,
        )
