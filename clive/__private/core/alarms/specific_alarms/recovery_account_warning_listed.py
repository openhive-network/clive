from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from clive.__private.core.alarms.alarm import Alarm, BaseAlarmData

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsData


@dataclass
class RecoveryAccountWarningListedAlarmData(BaseAlarmData):
    warning_recovery_account: str

    def get_titled_data(self) -> dict[str, str]:
        return {
            "Warning listed recovery account": self.warning_recovery_account,
        }


class RecoveryAccountWarningListed(Alarm[str, RecoveryAccountWarningListedAlarmData]):
    EXTENDED_ALARM_INFO = (
        "Your recovery account is listed as a warning account.\nYou should change it to another account."
    )

    def update_alarm_status(self, data: AccountAlarmsData) -> None:
        warning_recovery_accounts: Final[set[str]] = {"steem"}
        if data.recovery_account in warning_recovery_accounts:
            new_identifier = data.recovery_account
            if new_identifier == self.identifier:
                return

            self.set_alarm_active(
                new_identifier, RecoveryAccountWarningListedAlarmData(warning_recovery_account=data.recovery_account)
            )
            return

        self.set_alarm_inactive()

    def get_alarm_basic_info(self) -> str:
        return f"Your recovery account {self.ensure_alarm_data.warning_recovery_account} is listed as a warning account"
