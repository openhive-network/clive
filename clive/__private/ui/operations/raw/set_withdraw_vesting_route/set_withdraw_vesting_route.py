from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.widgets import Checkbox

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.placeholders_constants import PERCENT_PLACEHOLDER
from schemas.operations import SetWithdrawVestingRouteOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Vertical):
    """All the content of the screen, excluding the title."""


class SetWithdrawVestingRoute(RawOperationBaseScreen):
    """Screen to set/remove withdraw vesting route."""

    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self, receiver: str, percent: int, auto_vest: bool, cancel: bool = False) -> None:
        """
        Initialize the SetWithdrawVestingRoute screen.

        Args:
        ----
        receiver: receiver of withdraw route.
        percent: percent to sent to the receiver (0 if removing withdraw route).
        auto_vest: whether withdrawal with auto vest or no.
        cancel: whether the payment is cancelled or not.
        """
        super().__init__()

        self._to_account_input = AccountNameInput(label="to account", value=receiver, disabled=True)
        self._percent_input = IntegerInput(
            label="percent", value=percent, placeholder=PERCENT_PLACEHOLDER, disabled=True
        )
        self._auto_vest_input = Checkbox("auto vest", value=auto_vest, disabled=True)
        self._cancel = cancel

    def create_left_panel(self) -> ComposeResult:
        if not self._cancel:
            yield BigTitle("Set withdraw route")
        else:
            yield BigTitle("Remove withdraw route")
        with ScrollableContainer(), Body():
            with Horizontal(id="from-account-display"):
                yield InputLabel("from")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="from-label")
            yield self._to_account_input
            if not self._cancel:
                yield self._percent_input
            with Container(id="container-with-checkbox"):
                yield self._auto_vest_input

    def _create_operation(self) -> SetWithdrawVestingRouteOperation | None:
        percent = self._percent_input.value
        if percent is not None:
            percent *= 100

        return SetWithdrawVestingRouteOperation(
            from_account=self.app.world.profile_data.working_account.name,
            to_account=self._to_account_input.value,
            auto_vest=self._auto_vest_input.value,
            percent=percent,
        )
