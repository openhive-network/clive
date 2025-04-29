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
from clive.__private.models.schemas import HiveDateTime

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsData


@dataclass
class GovernanceVotingExpirationAlarmData(AlarmDataWithEndDate):
    END_DATE_LABEL: ClassVar[str] = "Expiration date"


class GovernanceVotingExpiration(Alarm[DateTimeAlarmIdentifier, GovernanceVotingExpirationAlarmData]):
    ALARM_DESCRIPTION = GOVERNANCE_VOTING_EXPIRATION_ALARM_DESCRIPTION
    FIX_ALARM_INFO = "You should cast votes for witnesses and proposals or set a proxy."

    WARNING_PERIOD_IN_DAYS: Final[int] = 31

    def update_alarm_status(self, data: AccountAlarmsData) -> None:
        expiration: datetime = data.governance_vote_expiration_ts
        if is_null_date(expiration):
            self.disable_alarm()
            return

        alarm_data = GovernanceVotingExpirationAlarmData(end_date=expiration)
        if alarm_data.time_left > timedelta(days=self.WARNING_PERIOD_IN_DAYS):
            self.disable_alarm()
            return

        new_identifier = DateTimeAlarmIdentifier(value=HiveDateTime(expiration))
        self.enable_alarm(new_identifier, alarm_data)
        return

    def get_alarm_basic_info(self) -> str:
        return f"Governance votes will expire in {self.alarm_data_ensure.pretty_time_left}"
