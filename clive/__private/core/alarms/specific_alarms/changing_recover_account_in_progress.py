from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from clive.__private.core.alarms.alarm import Alarm, BaseAlarmData
from clive.__private.core.constants import HIVE_OWNER_AUTH_RECOVERY_PERIOD_DAYS
from clive.__private.core.formatters.humanize import humanize_datetime

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsProcessedData


@dataclass
class ChangingRecoveryAccountInProgressAlarmData(BaseAlarmData):
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
            "Start date": self.pretty_start_date,
            "Effective date": self.pretty_effective_date,
            "New recovery account": self.new_recovery_account,
        }


class ChangingRecoveryAccountInProgress(Alarm[datetime, ChangingRecoveryAccountInProgressAlarmData]):
    EXTENDED_ALARM_INFO = (
        "Setting recovery account is in progress.\nYou can cancel it by set recovery account to the old one."
    )

    def update_alarm_status(self, data: AccountAlarmsProcessedData) -> None:
        request = data.change_recovery_account_request
        if request is not None:
            new_identifier = request.effective_on

            if new_identifier == self.identifier:
                return

            self.set_alarm_active(
                new_identifier,
                ChangingRecoveryAccountInProgressAlarmData(
                    start_date=self._calculate_start_process_date(request.effective_on),
                    effective_date=request.effective_on,
                    new_recovery_account=request.recovery_account,
                ),
            )
            return

        self.set_alarm_inactive()

    def get_alarm_basic_info(self) -> str:
        return f"Setting of recovery account to {self.ensure_alarm_data.new_recovery_account} is in progress"

    def _calculate_start_process_date(self, effective_data: datetime) -> datetime:
        return effective_data + timedelta(days=HIVE_OWNER_AUTH_RECOVERY_PERIOD_DAYS)
