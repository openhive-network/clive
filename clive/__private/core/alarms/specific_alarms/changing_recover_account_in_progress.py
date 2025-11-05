from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.alarms.alarm import Alarm
from clive.__private.core.alarms.alarm_data import AlarmDataWithStartAndEndDate
from clive.__private.core.alarms.alarm_identifier import DateTimeAlarmIdentifier
from clive.__private.core.constants.alarms import CHANGING_RECOVERY_ACCOUNT_IN_PROGRESS_ALARM_DESCRIPTION
from clive.__private.core.constants.node import CHANGE_RECOVERY_ACCOUNT_PENDING_DAYS

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsData


@dataclass
class ChangingRecoveryAccountInProgressAlarmData(AlarmDataWithStartAndEndDate):
    END_DATE_LABEL: ClassVar[str] = "Effective date"
    NEW_RECOVERY_ACCOUNT_LABEL: ClassVar[str] = "New recovery account"

    new_recovery_account: str

    def get_titled_data(self) -> dict[str, str]:
        return super().get_titled_data() | {self.NEW_RECOVERY_ACCOUNT_LABEL: self.new_recovery_account}


class ChangingRecoveryAccountInProgress(Alarm[DateTimeAlarmIdentifier, ChangingRecoveryAccountInProgressAlarmData]):
    ALARM_DESCRIPTION = CHANGING_RECOVERY_ACCOUNT_IN_PROGRESS_ALARM_DESCRIPTION
    FIX_ALARM_INFO = "You can cancel it by setting a recovery account to the previous one."

    def update_alarm_status(self, data: AccountAlarmsData) -> None:
        request = data.change_recovery_account_request

        if request is None:
            self.disable_alarm()
            return

        new_identifier = DateTimeAlarmIdentifier(value=request.effective_on)
        self.enable_alarm(
            new_identifier,
            ChangingRecoveryAccountInProgressAlarmData(
                start_date=self._calculate_start_process_date(request.effective_on),
                end_date=request.effective_on,
                new_recovery_account=request.recovery_account,
            ),
        )
        return

    def get_alarm_basic_info(self) -> str:
        return f"Setting the recovery account to {self.alarm_data_ensure.new_recovery_account} is in progress"

    def _calculate_start_process_date(self, effective_data: datetime) -> datetime:
        return effective_data - timedelta(days=CHANGE_RECOVERY_ACCOUNT_PENDING_DAYS)
