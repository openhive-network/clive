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
    """
    Data class for the RecoveryAccountWarningListed alarm.

    Args:
        warning_recovery_account: The recovery account that is listed as a warning account.
        WARNING_LISTED_ACCOUNT_LABEL: A label for the warning listed recovery account.
    """

    WARNING_LISTED_ACCOUNT_LABEL: ClassVar[str] = "Warning listed recovery account"

    warning_recovery_account: str

    def get_titled_data(self) -> dict[str, str]:
        """
        Return a dictionary with the warning recovery account labeled.

        Returns:
            dict: A dictionary containing the warning recovery account with a label.
        """
        return {self.WARNING_LISTED_ACCOUNT_LABEL: self.warning_recovery_account} | super().get_titled_data()


class RecoveryAccountWarningListedAlarmIdentifier(AlarmIdentifier):
    """
    Class to identify the alarm.

    Args:
        recovery_account: The recovery account that is listed as a warning account.
    """

    recovery_account: str


class RecoveryAccountWarningListed(
    Alarm[RecoveryAccountWarningListedAlarmIdentifier, RecoveryAccountWarningListedAlarmData]
):
    """
    Class to handle the Recovery Account Warning Listed alarm.

    Args:
        WARNING_RECOVERY_ACCOUNTS: A set of recovery accounts that are considered warning accounts.
    """

    WARNING_RECOVERY_ACCOUNTS: Final[set[str]] = {"steem"}

    ALARM_DESCRIPTION = RECOVERY_ACCOUNT_WARNING_LISTED_ALARM_DESCRIPTION
    FIX_ALARM_INFO = f"You should change it to account other than \\{list(WARNING_RECOVERY_ACCOUNTS)}"

    def update_alarm_status(self, data: AccountAlarmsData) -> None:
        """
        Update the status of the alarm based on the provided account data.

        Args:
            data: The account data containing the recovery account information.

        Returns:
            None: If the recovery account is not in the warning list, the alarm is disabled.
        """
        if data.recovery_account not in self.WARNING_RECOVERY_ACCOUNTS:
            self.disable_alarm()
            return

        new_identifier = RecoveryAccountWarningListedAlarmIdentifier(recovery_account=data.recovery_account)
        self.enable_alarm(
            new_identifier, RecoveryAccountWarningListedAlarmData(warning_recovery_account=data.recovery_account)
        )
        return

    def get_alarm_basic_info(self) -> str:
        """
        Get basic information about the alarm.

        Returns:
            str: A string containing the basic information about the recovery account warning.
        """
        return f"Your recovery account {self.alarm_data_ensure.warning_recovery_account} is listed as a warning account"
