from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.settings import safe_settings
from clive.__private.storage.current_model import ProfileStorageModel
from clive.__private.storage.migrations import v0
from clive.__private.storage.service import PersistentStorageService
from clive_local_tools.data.constants import ALT_WORKING_ACCOUNT1_PASSWORD
from clive_local_tools.storage_migration.helpers import copy_profile_without_alarms_and_operations
from clive_local_tools.testnet_block_log import ALT_WORKING_ACCOUNT1_NAME, WATCHED_ACCOUNTS_NAMES

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


@pytest.fixture(autouse=True)
def _prepare_profiles_for_loading_in_old_version() -> None:
    copy_profile_without_alarms_and_operations(safe_settings.data_path)


PROFILE_NAME: Final[str] = ALT_WORKING_ACCOUNT1_NAME
PROFILE_PASSWORD: Final[str] = ALT_WORKING_ACCOUNT1_PASSWORD
OTHER_ACCOUNT: Final[str] = WATCHED_ACCOUNTS_NAMES[0]


def _get_profile_file_version(profile_name: str) -> int:
    paths = PersistentStorageService._get_filepaths(profile_name=PROFILE_NAME, file_type="profile")
    assert len(paths) == 1, f"Profile {profile_name} should have exactly one file"
    info = next(iter(paths))
    return info.version()


async def test_unlock_and_migrate(cli_tester_locked: CLITester) -> None:
    # ARRANGE
    cli_tester_locked.unlock(profile_name=PROFILE_NAME, password_stdin=PROFILE_PASSWORD)
    cli_tester = cli_tester_locked
    assert _get_profile_file_version(PROFILE_NAME) == v0.ProfileStorageModel.get_this_version(), (
        f"before migration profile should be stored in version {v0.ProfileStorageModel.get_this_version()}"
    )

    # ACT & ASSERT
    result = cli_tester.show_profile()  # remove after resolving issue https://gitlab.syncad.com/hive/clive/-/issues/413
    assert f"Profile name: {PROFILE_NAME}" in result.output, "profile is not loaded"
    assert _get_profile_file_version(PROFILE_NAME) == ProfileStorageModel.get_this_version(), (
        f"after migration profile should be stored in version {ProfileStorageModel.get_this_version()}"
    )


async def test_save_changes_in_migrated_profile(cli_tester_locked: CLITester) -> None:
    # ARRANGE
    cli_tester_locked.unlock(profile_name=PROFILE_NAME, password_stdin=PROFILE_PASSWORD)
    cli_tester = cli_tester_locked

    # ACT & ASSERT
    cli_tester.configure_tracked_account_add(account_name=OTHER_ACCOUNT)
    result = cli_tester.show_profile()
    assert OTHER_ACCOUNT in result.output, f"{OTHER_ACCOUNT} should be added to tracked accounts"

    cli_tester.configure_tracked_account_remove(account_name=OTHER_ACCOUNT)
    result = cli_tester.show_profile()
    assert OTHER_ACCOUNT in result.output, f"{OTHER_ACCOUNT} should be removed from tracked accounts"
