from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from clive.__private.core.alarms.alarm import Alarm, BaseAlarmData

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsData


@dataclass
class GovernanceNoActiveVotesAlarmData(BaseAlarmData):
    expiration_date: datetime

    @property
    def pretty_expiration_date(self) -> str:
        return "Never(no active votes)"

    def get_titled_data(self) -> dict[str, str]:
        return {
            "Expiration date": self.pretty_expiration_date,
        }


@dataclass
class GovernanceNoActiveVotes(Alarm[datetime, GovernanceNoActiveVotesAlarmData]):
    EXTENDED_ALARM_INFO = (
        "You have no active governance votes.\nYou should cast votes for witnesses and proposals or set a proxy.\n"
    )

    def update_alarm_status(self, data: AccountAlarmsData) -> None:
        no_votes_date = datetime(1969, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        expiration = self._normalize_datetime(data.governance_vote_expiration_ts)
        if expiration == no_votes_date:
            if self.is_harmless:
                return

            self.set_alarm_active(expiration, GovernanceNoActiveVotesAlarmData(expiration_date=expiration))
            return

        self.set_alarm_inactive()

    def get_alarm_basic_info(self) -> str:
        return "No active governance votes"

    @staticmethod
    def _normalize_datetime(date: datetime) -> datetime:
        return date.replace(microsecond=0, tzinfo=timezone.utc)
