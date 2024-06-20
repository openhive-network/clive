from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.alarms.alarm import Alarm, BaseAlarmData
from clive.__private.core.constants import CHANGE_RECOVERY_ACCOUNT_PENDING_DAYS
from clive.__private.core.formatters.humanize import humanize_datetime

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsData


@dataclass
class ChangingRecoveryAccountInProgressAlarmData(BaseAlarmData):
    START_DATE_LABEL: ClassVar[str] = "Start date"
    EFFECTIVE_DATE_LABEL: ClassVar[str] = "Effective date"
    NEW_RECOVERY_ACCOUNT_LABEL: ClassVar[str] = "New recovery account"

    start_date: datetime
    effective_date: datetime
    new_recovery_account: str

    @property
    def pretty_start_date(self) -> str:
        return humanize_datetime(self.start_date)

    @property
    def pretty_effective_date(self) -> str:
        return humanize_datetime(self.effective_date)

    def get_titled_data(self) -> dict[str, str]:
        return {
            self.START_DATE_LABEL: self.pretty_start_date,
            self.EFFECTIVE_DATE_LABEL: self.pretty_effective_date,
            self.NEW_RECOVERY_ACCOUNT_LABEL: self.new_recovery_account,
        }


class ChangingRecoveryAccountInProgress(Alarm[datetime, ChangingRecoveryAccountInProgressAlarmData]):
    EXTENDED_ALARM_INFO = "Changing recovery account is in progress."
    FIX_ALARM_INFO = "You can cancel it by set recovery account to the previous one."

    def update_alarm_status(self, data: AccountAlarmsData) -> None:
        request = data.change_recovery_account_request

        if request is None:
            self.disable_alarm()
            return

        new_identifier = request.effective_on
        self.enable_alarm(
            new_identifier,
            ChangingRecoveryAccountInProgressAlarmData(
                start_date=self._calculate_start_process_date(request.effective_on),
                effective_date=request.effective_on,
                new_recovery_account=request.recovery_account,
            ),
        )
        return

    def get_alarm_basic_info(self) -> str:
        return f"Setting the recovery account to {self.alarm_data_ensure.new_recovery_account} is in progress"

    def _calculate_start_process_date(self, effective_data: datetime) -> datetime:
        return effective_data - timedelta(days=CHANGE_RECOVERY_ACCOUNT_PENDING_DAYS)
