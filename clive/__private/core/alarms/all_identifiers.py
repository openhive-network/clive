from __future__ import annotations

from clive.__private.core.alarms.alarm_identifier import DateTimeAlarmIdentifier
from clive.__private.core.alarms.specific_alarms.recovery_account_warning_listed import (
    RecoveryAccountWarningListedAlarmIdentifier,
)

AllAlarmIdentifiers = DateTimeAlarmIdentifier | RecoveryAccountWarningListedAlarmIdentifier
