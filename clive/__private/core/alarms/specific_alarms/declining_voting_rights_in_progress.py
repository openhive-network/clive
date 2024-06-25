from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.alarms.alarm import Alarm
from clive.__private.core.alarms.specific_alarms.alarms_with_date_ranges import (
    AlarmDataWithStartAndEndDate,
)
from clive.__private.core.constants import DECLINE_VOTING_RIGHTS_PENDING_DAYS

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsData


@dataclass
class DecliningVotingRightsInProgressAlarmData(AlarmDataWithStartAndEndDate):
    END_DATE_LABEL: ClassVar[str] = "Effective date"


@dataclass
class DecliningVotingRightsInProgress(Alarm[datetime, DecliningVotingRightsInProgressAlarmData]):
    EXTENDED_ALARM_INFO = (
        "The decline voting rights operation is in progress.\n"
        "After effective date the operation is irreversible.\n"
        "The operation prevents voting on witnesses, proposals, posts and comments."
    )
    FIX_ALARM_INFO = (
        "You can cancel it by creating a decline operation with the `decline` value set to false before effective date."
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
                start_date=self._calculate_start_process_date(effective_date), end_date=effective_date
            ),
        )
        return

    def get_alarm_basic_info(self) -> str:
        return "Declining voting rights is underway for the account"

    def _calculate_start_process_date(self, effective_date: datetime) -> datetime:
        return effective_date - timedelta(days=DECLINE_VOTING_RIGHTS_PENDING_DAYS)
