from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.alarms.alarm import Alarm, BaseAlarmData
from clive.__private.core.date_utils import is_null_date

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsData


@dataclass
class GovernanceNoActiveVotesAlarmData(BaseAlarmData):
    EXPIRATION_DATE_LABEL: ClassVar[str] = "Expiration date"

    expiration_date: datetime

    @property
    def pretty_expiration_date(self) -> str:
        return "Never (no active votes)"

    def get_titled_data(self) -> dict[str, str]:
        return {
            self.EXPIRATION_DATE_LABEL: self.pretty_expiration_date,
        }


@dataclass
class GovernanceNoActiveVotes(Alarm[datetime, GovernanceNoActiveVotesAlarmData]):
    FIX_ALARM_INFO = "You should cast votes for witnesses and proposals or set a proxy."

    def update_alarm_status(self, data: AccountAlarmsData) -> None:
        expiration = data.governance_vote_expiration_ts
        if is_null_date(expiration):
            new_identifier = expiration
            self.enable_alarm(new_identifier, GovernanceNoActiveVotesAlarmData(expiration_date=expiration))
            return

        self.disable_alarm()

    def get_alarm_basic_info(self) -> str:
        return "No active governance votes"
