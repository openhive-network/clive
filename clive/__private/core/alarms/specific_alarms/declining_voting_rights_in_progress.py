from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.alarms.alarm import Alarm
from clive.__private.core.alarms.alarm_data import (
    AlarmDataWithStartAndEndDate,
)
from clive.__private.core.alarms.specific_alarms.alarm_descriptions import (
    DECLINING_VOTING_RIGHTS_IN_PROGRESS_ALARM_DESCRIPTION,
)
from clive.__private.core.constants import DECLINE_VOTING_RIGHTS_PENDING_DAYS

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsData


@dataclass
class DecliningVotingRightsInProgressAlarmData(AlarmDataWithStartAndEndDate):
    END_DATE_LABEL: ClassVar[str] = "Effective date"


class DecliningVotingRightsInProgress(Alarm[datetime, DecliningVotingRightsInProgressAlarmData]):
    ALARM_DESCRIPTION = DECLINING_VOTING_RIGHTS_IN_PROGRESS_ALARM_DESCRIPTION
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
