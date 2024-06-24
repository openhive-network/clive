from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, ClassVar, Final

from clive.__private.core.alarms.alarm import Alarm, BaseAlarmData
from clive.__private.core.date_utils import is_null_date, utc_now
from clive.__private.core.formatters.humanize import humanize_datetime, humanize_natural_time

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsData


@dataclass
class GovernanceVotingExpirationAlarmData(BaseAlarmData):
    EXPIRATION_DATE_LABEL: ClassVar[str] = "Expiration date"
    TIME_LEFT_LABEL: ClassVar[str] = "Time left"

    expiration_date: datetime

    @property
    def pretty_expiration_date(self) -> str:
        return humanize_datetime(self.expiration_date)

    @property
    def pretty_time_left(self) -> str:
        return humanize_natural_time(-self.time_left)

    @property
    def time_left(self) -> timedelta:
        return self.expiration_date - utc_now()

    def get_titled_data(self) -> dict[str, str]:
        return {
            self.EXPIRATION_DATE_LABEL: self.pretty_expiration_date,
            self.TIME_LEFT_LABEL: self.pretty_time_left,
        }


@dataclass
class GovernanceVotingExpiration(Alarm[datetime, GovernanceVotingExpirationAlarmData]):
    EXTENDED_ALARM_INFO = "The governance votes are valid one year.\nYour governance votes are about to expire."
    FIX_ALARM_INFO = "You should cast votes for witnesses and proposals or set a proxy."

    WARNING_PERIOD_IN_DAYS: Final[int] = 31

    def update_alarm_status(self, data: AccountAlarmsData) -> None:
        expiration: datetime = data.governance_vote_expiration_ts
        if is_null_date(expiration):
            self.disable_alarm()
            return

        alarm_data = GovernanceVotingExpirationAlarmData(expiration_date=expiration)
        if alarm_data.time_left > timedelta(days=self.WARNING_PERIOD_IN_DAYS):
            self.disable_alarm()
            return

        new_identifier = expiration
        self.enable_alarm(new_identifier, alarm_data)
        return

    def get_alarm_basic_info(self) -> str:
        return f"Governance votes will expire in {self.alarm_data_ensure.pretty_time_left}"
