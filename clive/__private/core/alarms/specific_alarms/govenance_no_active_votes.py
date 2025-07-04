from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING

from clive.__private.core.alarms.alarm import Alarm
from clive.__private.core.alarms.alarm_data import AlarmDataNeverExpiresWithoutAction
from clive.__private.core.alarms.alarm_identifier import DateTimeAlarmIdentifier
from clive.__private.core.constants.alarm_descriptions import GOVERNANCE_COMMON_ALARM_DESCRIPTION
from clive.__private.core.date_utils import is_null_date

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsData


@dataclass
class GovernanceNoActiveVotesAlarmData(AlarmDataNeverExpiresWithoutAction):
    """
    Class representing the data for the GovernanceNoActiveVotes alarm.

    Args:
        expiration_date: The date when the governance vote expires.
    """

    expiration_date: datetime


class GovernanceNoActiveVotes(Alarm[DateTimeAlarmIdentifier, GovernanceNoActiveVotesAlarmData]):
    """Class representing an alarm for no active governance votes."""

    ALARM_DESCRIPTION = GOVERNANCE_COMMON_ALARM_DESCRIPTION
    FIX_ALARM_INFO = "You should cast votes for witnesses and proposals or set a proxy."

    def update_alarm_status(self, data: AccountAlarmsData) -> None:
        """
        Update the status of the alarm based on the provided account alarms data.

        Args:
            data: The account alarms data containing governance vote expiration information.

        Returns:
            None
        """
        expiration = data.governance_vote_expiration_ts
        if is_null_date(expiration):
            new_identifier = DateTimeAlarmIdentifier(value=expiration)
            self.enable_alarm(new_identifier, GovernanceNoActiveVotesAlarmData(expiration_date=expiration))
            return

        self.disable_alarm()

    def get_alarm_basic_info(self) -> str:
        """
        Return a basic description of the alarm.

        Returns:
            str: A string indicating that there are no active governance votes.
        """
        return "No active governance votes"
