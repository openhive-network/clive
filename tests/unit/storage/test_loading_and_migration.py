from __future__ import annotations

from typing import Final

from clive.__private.core.alarms.specific_alarms.recovery_account_warning_listed import (
    RecoveryAccountWarningListedAlarmIdentifier,
)
from clive.__private.settings import safe_settings
from clive_local_tools.checkers.profile_checker import ProfileChecker
from clive_local_tools.data.constants import ALT_WORKING_ACCOUNT1_PASSWORD
from clive_local_tools.storage_migration import (
    OPERATION,
    copy_profile_with_alarms,
    copy_profile_with_operations,
    copy_profile_without_alarms_and_operations,
)
from clive_local_tools.testnet_block_log import ALT_WORKING_ACCOUNT1_NAME, ALT_WORKING_ACCOUNT2_NAME

PROFILE_NAME: Final[str] = ALT_WORKING_ACCOUNT1_NAME
PROFILE_PASSWORD: Final[str] = ALT_WORKING_ACCOUNT1_PASSWORD


async def test_migrate_profile_without_alarms_and_operations() -> None:
    # ARRANGE
    copy_profile_without_alarms_and_operations(safe_settings.data_path)

    async with ProfileChecker.from_password(PROFILE_NAME, PROFILE_PASSWORD) as profile_checker:
        # ACT
        profile = await profile_checker.profile

        # ASSERT
        assert profile.name == PROFILE_NAME, f"Profile with name {PROFILE_NAME} should be loaded"


async def test_migrate_profile_with_alarms() -> None:
    # ARRANGE
    copy_profile_with_alarms(safe_settings.data_path)

    async with ProfileChecker.from_password(PROFILE_NAME, PROFILE_PASSWORD) as profile_checker:
        # ACT
        profile = await profile_checker.profile

        # ASSERT
        assert profile.name == PROFILE_NAME, f"Profile with name {PROFILE_NAME} should be loaded"
        alarms = profile.accounts.working._alarms
        assert alarms.all_alarms, "Alarms should be loaded from older profile version"
        assert type(alarms.recovery_account_warning_listed.identifier) is RecoveryAccountWarningListedAlarmIdentifier, (
            "Alarm identifier should be of type RecoveryAccountWarningListedAlarmIdentifier"
        )
        assert alarms.recovery_account_warning_listed.identifier.recovery_account == ALT_WORKING_ACCOUNT2_NAME, (
            f"Alarm recovery account should be {ALT_WORKING_ACCOUNT2_NAME}"
        )


async def test_migrate_profile_with_operations() -> None:
    # ARRANGE
    copy_profile_with_operations(safe_settings.data_path)

    async with ProfileChecker.from_password(PROFILE_NAME, PROFILE_PASSWORD) as profile_checker:
        # ACT
        profile = await profile_checker.profile

        # ASSERT
        assert profile.name == PROFILE_NAME, f"Profile with name {PROFILE_NAME} should be loaded"
        assert profile.operations, "Operations should be loaded from older profile version"
        operation = profile.operations[0]
        assert operation == OPERATION, f"Operation should be `{OPERATION}`, but got `{operation}`"
