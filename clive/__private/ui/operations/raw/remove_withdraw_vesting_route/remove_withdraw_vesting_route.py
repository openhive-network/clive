from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal, ScrollableContainer, Vertical

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import PERCENT_PLACEHOLDER
from schemas.operations import SetWithdrawVestingRouteOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Vertical):
    """All the content of the screen, excluding the title."""


class RemoveWithdrawVestingRoute(RawOperationBaseScreen):
    """Screen to remove withdraw vesting route."""

    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self, receiver: str, percent: int, auto_vest: bool) -> None:
        """
        Initialize the RemoveWithdrawVestingRoute screen.

        Args:
        ----
        receiver: receiver of withdraw route.
        percent: percent to sent to the receiver.
        auto_vest: whether withdrawal with auto vest or no.
        """
        super().__init__()

        self._to_account_input = AccountNameInput(label="to account", value=receiver, disabled=True)
        self._percent_input = IntegerInput(
            label="percent", value=percent, placeholder=PERCENT_PLACEHOLDER, disabled=True
        )
        self._auto_vest_input = TextInput(label="auto vest", value=str(auto_vest))

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Remove withdraw route")
        with ScrollableContainer(), Body():
            with Horizontal(id="from-account-display"):
                yield InputLabel("from")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="from-label")
            yield self._to_account_input
            yield self._percent_input

    def _create_operation(self) -> SetWithdrawVestingRouteOperation | None:
        return SetWithdrawVestingRouteOperation(
            from_account=self.app.world.profile_data.working_account.name,
            to_account=self._to_account_input.value,
            auto_vest=self._auto_vest_input.value,
            percent=0,
        )
