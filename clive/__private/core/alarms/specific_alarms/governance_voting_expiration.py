from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, ClassVar, Final

from clive.__private.core.alarms.alarm import Alarm
from clive.__private.core.alarms.alarm_data import AlarmDataWithEndDate
from clive.__private.core.alarms.alarm_identifier import DateTimeAlarmIdentifier
from clive.__private.core.constants.alarm_descriptions import (
    GOVERNANCE_VOTING_EXPIRATION_ALARM_DESCRIPTION,
)
from clive.__private.core.date_utils import is_null_date

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsData


@dataclass
class GovernanceVotingExpirationAlarmData(AlarmDataWithEndDate):
    """
    Data class for governance voting expiration alarm.

    Args:
        END_DATE_LABEL: Label for the end date of the alarm.
    """

    END_DATE_LABEL: ClassVar[str] = "Expiration date"


class GovernanceVotingExpiration(Alarm[DateTimeAlarmIdentifier, GovernanceVotingExpirationAlarmData]):
    """
    Class representing an alarm for governance voting expiration.

    Args:
        WARNING_PERIOD_IN_DAYS: Number of days before the expiration when the alarm should trigger.
    """

    ALARM_DESCRIPTION = GOVERNANCE_VOTING_EXPIRATION_ALARM_DESCRIPTION
    FIX_ALARM_INFO = "You should cast votes for witnesses and proposals or set a proxy."

    WARNING_PERIOD_IN_DAYS: Final[int] = 31

    def update_alarm_status(self, data: AccountAlarmsData) -> None:
        """
        Update the status of the governance voting expiration alarm based on the provided data.

        Args:
            data: The data containing governance vote expiration timestamp.

        Returns:
            None
        """
        expiration: datetime = data.governance_vote_expiration_ts
        if is_null_date(expiration):
            self.disable_alarm()
            return

        alarm_data = GovernanceVotingExpirationAlarmData(end_date=expiration)
        if alarm_data.time_left > timedelta(days=self.WARNING_PERIOD_IN_DAYS):
            self.disable_alarm()
            return

        new_identifier = DateTimeAlarmIdentifier(value=expiration)
        self.enable_alarm(new_identifier, alarm_data)
        return

    def get_alarm_basic_info(self) -> str:
        """
        Get a basic description of the governance voting expiration alarm.

        Returns:
            A string describing the alarm.
        """
        return f"Governance votes will expire in {self.alarm_data_ensure.pretty_time_left}"
