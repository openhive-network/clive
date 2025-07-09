from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.constants.node import PERCENT_TO_REMOVE_WITHDRAW_ROUTE
from clive.__private.core.constants.precision import HIVE_PERCENT_PRECISION
from clive.__private.core.formatters.humanize import humanize_bool
from clive.__private.models.schemas import SetWithdrawVestingRouteOperation, Uint16t
from clive.__private.ui.dialogs.operation_summary.operation_summary_base_dialog import OperationSummaryBaseDialog
from clive.__private.ui.widgets.inputs.labelized_input import LabelizedInput

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.models.schemas import WithdrawRoute


class RemoveWithdrawVestingRouteDialog(OperationSummaryBaseDialog):
    """Dialog to remove withdraw vesting route."""

    def __init__(self, withdraw_route: WithdrawRoute) -> None:
        super().__init__("Remove withdraw vesting route")
        self._withdraw_route = withdraw_route

    @property
    def working_account_name(self) -> str:
        return self.profile.accounts.working.name

    def create_dialog_content(self) -> ComposeResult:
        yield LabelizedInput("From account", self.working_account_name)
        yield LabelizedInput("To account", self._withdraw_route.to_account)
        yield LabelizedInput("Percent", f"{self._withdraw_route.percent / HIVE_PERCENT_PRECISION:.2f} %")
        yield LabelizedInput("Auto vest", humanize_bool(self._withdraw_route.auto_vest))

    def _create_operation(self) -> SetWithdrawVestingRouteOperation:
        return SetWithdrawVestingRouteOperation(
            from_account=self.working_account_name,
            to_account=self._withdraw_route.to_account,
            auto_vest=self._withdraw_route.auto_vest,
            percent=PERCENT_TO_REMOVE_WITHDRAW_ROUTE,
        )
