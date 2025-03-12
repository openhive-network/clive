from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.constants.node import PERCENT_TO_REMOVE_WITHDRAW_ROUTE
from clive.__private.core.constants.precision import HIVE_PERCENT_PRECISION
from clive.__private.core.formatters.humanize import humanize_bool
from clive.__private.models.schemas import SetWithdrawVestingRouteOperation
from clive.__private.ui.screens.operations.operation_summary.operation_summary import OperationSummary
from clive.__private.ui.widgets.inputs.labelized_input import LabelizedInput
from schemas.fields.integers import Uint16t

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.models.schemas import WithdrawRoute


class RemoveWithdrawVestingRoute(OperationSummary):
    """Screen to remove withdraw vesting route."""

    SECTION_TITLE: ClassVar[str] = "Remove withdraw vesting route"

    def __init__(self, withdraw_route: WithdrawRoute) -> None:
        super().__init__()
        self._withdraw_route = withdraw_route

    @property
    def working_account_name(self) -> str:
        return self.profile.accounts.working.name

    def content(self) -> ComposeResult:
        yield LabelizedInput("From account", self.working_account_name)
        yield LabelizedInput("To account", self._withdraw_route.to_account)
        yield LabelizedInput("Percent", f"{self._withdraw_route.percent / HIVE_PERCENT_PRECISION :.2f} %")
        yield LabelizedInput("Auto vest", humanize_bool(self._withdraw_route.auto_vest))

    def _create_operation(self) -> SetWithdrawVestingRouteOperation:
        return SetWithdrawVestingRouteOperation(
            from_account=self.working_account_name,
            to_account=self._withdraw_route.to_account,
            auto_vest=self._withdraw_route.auto_vest,
            percent=Uint16t(PERCENT_TO_REMOVE_WITHDRAW_ROUTE),
        )
