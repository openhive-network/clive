from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.constants.node import VESTS_TO_REMOVE_POWER_DOWN
from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.models import Asset
from clive.__private.models.schemas import WithdrawVestingOperation
from clive.__private.ui.dialogs.operation_summary.operation_summary_base_dialog import OperationSummaryBaseDialog
from clive.__private.ui.widgets.inputs.labelized_input import LabelizedInput

if TYPE_CHECKING:
    from datetime import datetime

    from textual.app import ComposeResult

    from clive.__private.models import HpVestsBalance


class CancelPowerDownDialog(OperationSummaryBaseDialog):
    def __init__(self, next_power_down_date: datetime, next_power_down: HpVestsBalance) -> None:
        super().__init__("Cancel power down")
        self._next_power_down_date = next_power_down_date
        self._next_power_down = next_power_down

    def create_dialog_content(self) -> ComposeResult:
        yield LabelizedInput("Next power down", humanize_datetime(self._next_power_down_date))
        yield LabelizedInput("Power down [HP]", Asset.pretty_amount(self._next_power_down.hp_balance))
        yield LabelizedInput("Power down [VESTS]", Asset.pretty_amount(self._next_power_down.vests_balance))

    def _create_operation(self) -> WithdrawVestingOperation:
        return WithdrawVestingOperation(
            account=self.profile.accounts.working.name,
            vesting_shares=Asset.vests(VESTS_TO_REMOVE_POWER_DOWN),
        )
