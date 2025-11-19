from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.alarms.alarm import Alarm, AnyAlarm
from clive.__private.core.alarms.specific_alarms import (
    ChangingRecoveryAccountInProgress,
    DecliningVotingRightsInProgress,
    GovernanceNoActiveVotes,
    GovernanceVotingExpiration,
    RecoveryAccountWarningListed,
)

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsData


class AlarmsStorage:
    def __init__(self, alarms: list[AnyAlarm] | None = None) -> None:
        alarms_ = alarms or []
        self.governance_voting_expiration = self._get_or_create_alarm(alarms_, GovernanceVotingExpiration)
        self.recovery_account_warning_listed = self._get_or_create_alarm(alarms_, RecoveryAccountWarningListed)
        self.declining_voting_rights_in_progress = self._get_or_create_alarm(alarms_, DecliningVotingRightsInProgress)
        self.changing_recovery_account_in_progress = self._get_or_create_alarm(
            alarms_, ChangingRecoveryAccountInProgress
        )
        self.governance_no_active_votes = self._get_or_create_alarm(alarms_, GovernanceNoActiveVotes)
        self._is_updated = False

    def update_alarms_status(self, data: AccountAlarmsData) -> None:
        for alarm in self.all_alarms:
            alarm.update_alarm_status(data)
        self._is_updated = True

    @property
    def harmful_alarms(self) -> list[AnyAlarm]:
        return [alarm for alarm in self.all_alarms if alarm.is_active and not alarm.is_harmless]

    @property
    def all_alarms(self) -> list[AnyAlarm]:
        return [
            alarm for alarm in self.__dict__.values() if isinstance(alarm, Alarm)
        ]  # Use is_instance to avoid treat `is_updated` as an alarm

    @property
    def is_alarms_data_available(self) -> bool:
        return self._is_updated

    def _get_or_create_alarm[SpecificAlarmT: AnyAlarm](
        self, alarms: list[AnyAlarm], alarm_cls: type[SpecificAlarmT]
    ) -> SpecificAlarmT:
        for alarm in alarms:
            if isinstance(alarm, alarm_cls):
                return alarm
        return alarm_cls()
