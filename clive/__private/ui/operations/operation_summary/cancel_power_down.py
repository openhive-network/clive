from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Final

from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.ui.operations.operation_summary.operation_summary import OperationSummary
from clive.__private.ui.widgets.inputs.labelized_input import LabelizedInput
from clive.models import Asset
from schemas.operations import WithdrawVestingOperation

if TYPE_CHECKING:
    from datetime import datetime

    from textual.app import ComposeResult

    from clive.__private.core.commands.data_retrieval.hive_power_data import SharesBalance


CANCEL_POWER_DOWN_VESTS_VALUE: Final[Asset.Vests] = Asset.vests(0)


class CancelPowerDown(OperationSummary):
    BIG_TITLE: ClassVar[str] = "Cancel power down"

    def __init__(self, next_power_down_date: datetime, next_power_down: SharesBalance) -> None:
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
            vesting_shares=CANCEL_POWER_DOWN_VESTS_VALUE,
        )

    @property
    def working_account(self) -> str:
        return self.app.world.profile_data.working_account.name
