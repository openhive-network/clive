from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, ClassVar, Final

from clive.__private.core.alarms.alarm import Alarm, BaseAlarmData
from clive.__private.core.date_utils import utc_now
from clive.__private.core.formatters.humanize import humanize_datetime

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsData


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
    EXTENDED_ALARM_INFO = "The governance votes are valid one year.\nYour governance votes are about to expire."
    FIX_ALARM_INFO = "You should cast votes for witnesses and proposals or set a proxy."

    WARNING_PERIOD_IN_DAYS: Final[int] = 31

    def update_alarm_status(self, data: AccountAlarmsData) -> None:  # noqa: ARG002
        expiration = utc_now()
        self.enable_alarm(expiration, GovernanceVotingExpirationAlarmData(expiration_date=expiration))

    def get_alarm_basic_info(self) -> str:
        return f"Governance votes will expire in {self.alarm_data_ensure.days_left} day(s)"
