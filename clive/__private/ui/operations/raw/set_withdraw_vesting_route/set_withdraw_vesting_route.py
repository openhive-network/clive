from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer
from textual.widgets import Checkbox

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.placeholders_constants import PERCENT_PLACEHOLDER
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import SetWithdrawVestingRouteOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class SetWithdrawVestingRoute(RawOperationBaseScreen):
    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self) -> None:
        super().__init__()

        default_percent = get_default_from_model(SetWithdrawVestingRouteOperation, "percent", int)
        default_auto_vest = get_default_from_model(SetWithdrawVestingRouteOperation, "auto_vest", bool)

        self.__to_account_input = AccountNameInput(label="to account")
        self.__percent_input = IntegerInput(label="percent", value=default_percent, placeholder=PERCENT_PLACEHOLDER)
        self.__auto_vest_input = Checkbox("auto vest", value=default_auto_vest)

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Set withdraw vesting route")
            with ScrollableContainer(), Body():
                yield InputLabel("from")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="from-label")
                yield from self.__to_account_input.compose()
                yield from self.__percent_input.compose()
                yield self.__auto_vest_input

    def _create_operation(self) -> SetWithdrawVestingRouteOperation | None:
        percent = self.__percent_input.value
        if not percent:
            return None

        return SetWithdrawVestingRouteOperation(
            from_account=self.app.world.profile_data.name,
            to_account=self.__to_account_input.value,
            auto_vest=self.__auto_vest_input.value,
            percent=percent,
        )
