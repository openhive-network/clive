from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, ClassVar, Final

from clive.__private.core.alarms.alarm import Alarm, BaseAlarmData
from clive.__private.core.formatters.humanize import _is_null_date, humanize_datetime

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsProcessedData


@dataclass
class GovernanceVotingExpirationAlarmData(BaseAlarmData):
    EXPIRATION_DATE_LABEL: ClassVar[str] = "Expiration date"
    DAYS_LEFT_LABEL: ClassVar[str] = "Days left"

    expiration_date: datetime

    @property
    def pretty_expiration_date(self) -> str:
        return humanize_datetime(self.expiration_date)

    @property
    def days_left(self) -> int:
        current_time = datetime.now(timezone.utc)
        return (self.expiration_date - current_time).days

    def get_titled_data(self) -> dict[str, str]:
        return {
            self.EXPIRATION_DATE_LABEL: self.pretty_expiration_date,
            self.DAYS_LEFT_LABEL: str(self.days_left),
        }


@dataclass
class GovernanceVotingExpiration(Alarm[datetime, GovernanceVotingExpirationAlarmData]):
    EXTENDED_ALARM_INFO = (
        "The governance votes are valid one year.\n"
        "Your governance votes are about to expire.\n"
        "You should cast votes for witnesses and proposals or set a proxy."
    )
    WARNING_PERIOD_IN_DAYS: Final[int] = 31

    def update_alarm_status(self, data: AccountAlarmsProcessedData) -> None:
        expiration: datetime = data.governance_vote_expiration_ts
        if _is_null_date(expiration):
            self.disable_alarm()
            return

        alarm_data = GovernanceVotingExpirationAlarmData(expiration_date=expiration)

        if alarm_data.days_left > self.WARNING_PERIOD_IN_DAYS:
            self.disable_alarm()
            return

        new_identifier = expiration
        self.enable_alarm(new_identifier, alarm_data)
        return

    def get_alarm_basic_info(self) -> str:
        return f"Governance votes will expire in {self.alarm_data_ensure.days_left} day(s)"
