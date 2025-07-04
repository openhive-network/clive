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
    """Storage for alarms related to account activities."""

    def __init__(self, alarms: list[AnyAlarm] | None = None) -> None:
        """
        Initialize the AlarmsStorage with a list of alarms or creates default alarms if none are provided.

        Args:
            alarms: A list of existing alarms to initialize the storage with. If None, default alarms will be created.

        Returns:
            None
        """
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
        """
        Update the status of all alarms based on the provided data.

        Args:
            data: An instance of AccountAlarmsData containing the latest alarm data.

        Returns:
            None
        """
        for alarm in self.all_alarms:
            alarm.update_alarm_status(data)
        self._is_updated = True

    @property
    def harmful_alarms(self) -> list[AnyAlarm]:
        """
        Return a list of harmful alarms that are currently active.

        Returns:
            A list of active harmful alarms.
        """
        return [alarm for alarm in self.all_alarms if alarm.is_active and not alarm.is_harmless]

    @property
    def all_alarms(self) -> list[AnyAlarm]:
        """
        Return a list of all alarms stored in the AlarmsStorage.

        Returns:
            A list of all alarms, including both active and inactive ones.
        """
        return [
            alarm for alarm in self.__dict__.values() if isinstance(alarm, Alarm)
        ]  # Use is_instance to avoid treat `is_updated` as an alarm

    @property
    def is_alarms_data_available(self) -> bool:
        """
        Check if the alarms data has been updated since the last retrieval.

        Returns:
            bool: True if the alarms data has been updated, False otherwise.
        """
        return self._is_updated

    def _get_or_create_alarm(self, alarms: list[AnyAlarm], alarm_cls: type[AnyAlarm]) -> AnyAlarm:
        """
        Get an existing alarm of a specific type from the list or create a new one if it doesn't exist.

        Args:
            alarms: A list of existing alarms to search through.
            alarm_cls: The class type of the

        Returns:
            An instance of the specified alarm class, either found in the list or a new instance.
        """
        for alarm in alarms:
            if isinstance(alarm, alarm_cls):
                return alarm
        return alarm_cls()
