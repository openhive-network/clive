from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.constants.node import VESTS_TO_REMOVE_POWER_DOWN
from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.ui.operations.operation_summary.operation_summary import OperationSummary
from clive.__private.ui.widgets.inputs.labelized_input import LabelizedInput
from clive.models import Asset
from schemas.operations import WithdrawVestingOperation

if TYPE_CHECKING:
    from datetime import datetime

    from textual.app import ComposeResult

    from clive.models.hp_vests_balance import HpVestsBalance


class CancelPowerDown(OperationSummary):
    SECTION_TITLE: ClassVar[str] = "Cancel power down"

    def __init__(self, next_power_down_date: datetime, next_power_down: HpVestsBalance) -> None:
        super().__init__()
        self._next_power_down_date = next_power_down_date
        self._next_power_down = next_power_down

    def content(self) -> ComposeResult:
        yield LabelizedInput("Next power down", humanize_datetime(self._next_power_down_date))
        yield LabelizedInput("Power down [HP]", Asset.pretty_amount(self._next_power_down.hp_balance))
        yield LabelizedInput("Power down [VESTS]", Asset.pretty_amount(self._next_power_down.vests_balance))

    def _create_operation(self) -> WithdrawVestingOperation:
        return WithdrawVestingOperation(
            account=self.working_account,
            vesting_shares=VESTS_TO_REMOVE_POWER_DOWN,
        )

    @property
    def working_account(self) -> str:
        return self.profile_data.working_account.name
