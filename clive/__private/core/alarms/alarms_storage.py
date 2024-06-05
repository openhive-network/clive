from __future__ import annotations

from typing import TYPE_CHECKING, Any

from clive.__private.core.alarms.alarm import Alarm
from clive.__private.core.alarms.specific_alarms import GovernanceVotingExpiration

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsProcessedData


class AlarmsStorage:
    def __init__(self) -> None:
        self.governance_voting_expiration = GovernanceVotingExpiration(is_fix_possible_using_clive=True)
        self._is_updated = False

    def update_alarms_status(self, data: AccountAlarmsProcessedData) -> None:
        for alarm in self.all_alarms:
            alarm.update_alarm_status(data)
        self._is_updated = True

    @property
    def harmful_alarms(self) -> list[Alarm[Any, Any]]:
        return [alarm for alarm in self.all_alarms if alarm.is_active and not alarm.is_harmless]

    @property
    def all_alarms(self) -> list[Alarm[Any, Any]]:
        return [
            alarm for alarm in self.__dict__.values() if isinstance(alarm, Alarm)
        ]  # Use is_instance to avoid treat `is_updated` as an alarm

    @property
    def is_alarms_data_available(self) -> bool:
        return self._is_updated
