from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Final

from clive.__private.core.alarms.alarm import Alarm
from clive.__private.core.alarms.alarm_data import AlarmDataNeverExpiresWithoutAction
from clive.__private.core.alarms.alarm_identifier import AlarmIdentifier
from clive.__private.core.constants.alarm_descriptions import RECOVERY_ACCOUNT_WARNING_LISTED_ALARM_DESCRIPTION

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsData


@dataclass
class RecoveryAccountWarningListedAlarmData(AlarmDataNeverExpiresWithoutAction):
    WARNING_LISTED_ACCOUNT_LABEL: ClassVar[str] = "Warning listed recovery account"

    warning_recovery_account: str

    def get_titled_data(self) -> dict[str, str]:
        return {self.WARNING_LISTED_ACCOUNT_LABEL: self.warning_recovery_account} | super().get_titled_data()


class RecoveryAccountWarningListedAlarmIdentifier(AlarmIdentifier, tag=True):
    recovery_account: str


class RecoveryAccountWarningListed(
    Alarm[RecoveryAccountWarningListedAlarmIdentifier, RecoveryAccountWarningListedAlarmData]
):
    WARNING_RECOVERY_ACCOUNTS: Final[set[str]] = {"steem"}

    ALARM_DESCRIPTION = RECOVERY_ACCOUNT_WARNING_LISTED_ALARM_DESCRIPTION
    FIX_ALARM_INFO = f"You should change it to account other than \\{list(WARNING_RECOVERY_ACCOUNTS)}"

    def update_alarm_status(self, data: AccountAlarmsData) -> None:
        if data.recovery_account not in self.WARNING_RECOVERY_ACCOUNTS:
            self.disable_alarm()
            return

        new_identifier = RecoveryAccountWarningListedAlarmIdentifier(recovery_account=data.recovery_account)
        self.enable_alarm(
            new_identifier, RecoveryAccountWarningListedAlarmData(warning_recovery_account=data.recovery_account)
        )
        return

    def get_alarm_basic_info(self) -> str:
        return f"Your recovery account {self.alarm_data_ensure.warning_recovery_account} is listed as a warning account"
