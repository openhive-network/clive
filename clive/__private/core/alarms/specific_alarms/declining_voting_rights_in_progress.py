from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.alarms.alarm import Alarm
from clive.__private.core.alarms.alarm_data import AlarmDataWithStartAndEndDate
from clive.__private.core.alarms.alarm_identifier import DateTimeAlarmIdentifier
from clive.__private.core.constants.alarm_descriptions import DECLINING_VOTING_RIGHTS_IN_PROGRESS_ALARM_DESCRIPTION
from clive.__private.core.constants.node import DECLINE_VOTING_RIGHTS_PENDING_DAYS

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsData


@dataclass
class DecliningVotingRightsInProgressAlarmData(AlarmDataWithStartAndEndDate):
    """
    Class representing the data for the Declining Voting Rights In Progress alarm.

    Args:
        END_DATE_LABEL: Label for the end date of the alarm.
    """

    END_DATE_LABEL: ClassVar[str] = "Effective date"


class DecliningVotingRightsInProgress(Alarm[DateTimeAlarmIdentifier, DecliningVotingRightsInProgressAlarmData]):
    """Class representing an alarm for declining voting rights in progress."""

    ALARM_DESCRIPTION = DECLINING_VOTING_RIGHTS_IN_PROGRESS_ALARM_DESCRIPTION
    FIX_ALARM_INFO = (
        "You can cancel it by creating a decline operation with the `decline` value set to false before effective date."
    )

    def update_alarm_status(self, data: AccountAlarmsData) -> None:
        """
        Update the status of the Declining Voting Rights In Progress alarm based on the provided data.

        Args:
            data: AccountAlarmsData containing the information to update the alarm status.

        Returns:
            None
        """
        request = data.decline_voting_rights
        if not request:
            self.disable_alarm()
            return

        effective_date = request.effective_date
        new_identifier = DateTimeAlarmIdentifier(value=effective_date)
        self.enable_alarm(
            new_identifier,
            DecliningVotingRightsInProgressAlarmData(
                start_date=self._calculate_start_process_date(effective_date), end_date=effective_date
            ),
        )
        return

    def get_alarm_basic_info(self) -> str:
        """
        Get basic information about the Declining Voting Rights In Progress alarm.

        Returns:
            A string containing basic information about the alarm.
        """
        return "Declining voting rights is underway for the account"

    def _calculate_start_process_date(self, effective_date: datetime) -> datetime:
        """
        Calculate the start date for the declining voting rights process.

        Args:
            effective_date: The effective date of the decline voting rights request.

        Returns:
            A datetime object representing the start date of the process.
        """
        return effective_date - timedelta(days=DECLINE_VOTING_RIGHTS_PENDING_DAYS)
