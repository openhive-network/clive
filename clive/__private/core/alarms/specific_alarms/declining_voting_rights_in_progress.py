from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.alarms.alarm import Alarm, BaseAlarmData
from clive.__private.core.constants import DECLINE_VOTING_RIGHTS_PENDING_DAYS
from clive.__private.core.formatters.humanize import humanize_datetime

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsData


@dataclass
class DecliningVotingRightsInProgressAlarmData(BaseAlarmData):
    START_DATE_LABEL: ClassVar[str] = "Start date"
    EFFECTIVE_DATE_LABEL: ClassVar[str] = "Effective date"

    start_date: datetime
    effective_date: datetime

    @property
    def pretty_start_date(self) -> str:
        return humanize_datetime(self.start_date)

    @property
    def pretty_effective_date(self) -> str:
        return humanize_datetime(self.effective_date)

    def get_titled_data(self) -> dict[str, str]:
        return {
            self.START_DATE_LABEL: self.pretty_start_date,
            self.EFFECTIVE_DATE_LABEL: self.pretty_effective_date,
        }


@dataclass
class DecliningVotingRightsInProgress(Alarm[datetime, DecliningVotingRightsInProgressAlarmData]):
    EXTENDED_ALARM_INFO = (
        "The decline voting rights operation is in progress.\n"
        "You can cancel it by creating a decline operation with the `decline` value set to false before effective date.\n"
        "After effective date the operation is irreversible."
    )

    def update_alarm_status(self, data: AccountAlarmsData) -> None:
        request = data.decline_voting_rights
        if not request:
            self.disable_alarm()
            return

        effective_date = request.effective_date
        new_identifier = effective_date
        self.enable_alarm(
            new_identifier,
            DecliningVotingRightsInProgressAlarmData(
                start_date=self._calculate_start_process_date(effective_date), effective_date=effective_date
            ),
        )
        return

    def get_alarm_basic_info(self) -> str:
        return "Declining voting rights is underway for the account"

    def _calculate_start_process_date(self, effective_date: datetime) -> datetime:
        return effective_date - timedelta(days=DECLINE_VOTING_RIGHTS_PENDING_DAYS)
