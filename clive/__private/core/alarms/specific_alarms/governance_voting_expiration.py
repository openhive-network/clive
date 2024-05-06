from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Final

from clive.__private.core.alarms.alarm import Alarm, BaseAlarmData
from clive.__private.core.formatters.humanize import humanize_datetime

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsProcessedData


@dataclass
class GovernanceVotingExpirationAlarmData(BaseAlarmData):
    expiration_date: datetime
    days_left: int

    @property
    def pretty_expiration_date(self) -> str:
        return humanize_datetime(self.expiration_date)

    def get_titled_data(self) -> dict[str, str]:
        return {
            "Expiration date": self.pretty_expiration_date,
            "Days left": str(self.days_left),
        }


@dataclass
class GovernanceVotingExpiration(Alarm[datetime, GovernanceVotingExpirationAlarmData]):
    EXTENDED_ALARM_INFO = (
        "The governance votes are valid one year.\n"
        "Your governance votes are about to expire.\n"
        "You should cast votes for witnesses and proposals or set a proxy.\n"
    )

    def update_alarm_status(self, data: AccountAlarmsProcessedData) -> None:
        expiration: datetime = data.governance_vote_expiration_ts
        never_voted_date = datetime(1969, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        if expiration == never_voted_date:
            self.set_alarm_inactive()
            return

        warning_period_in_days: Final[int] = 31
        current_time = self._normalize_datetime(datetime.utcnow())
        days_left = (expiration - current_time).days
        if days_left <= warning_period_in_days:
            new_identifier = expiration
            if self.identifier == new_identifier:
                return
            self.set_alarm_active(
                new_identifier, GovernanceVotingExpirationAlarmData(expiration_date=expiration, days_left=days_left)
            )
            return

        self.set_alarm_inactive()

    def get_alarm_basic_info(self) -> str:
        return f"Governance votes will expire in {self.ensure_alarm_data.days_left} day(s)"

    @staticmethod
    def _normalize_datetime(date: datetime) -> datetime:
        return date.replace(microsecond=0, tzinfo=timezone.utc)
