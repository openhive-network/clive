from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.settings import safe_settings
from clive_local_tools.cli.checkers import assert_no_exit_code_error
from clive_local_tools.storage_migration.helpers import ALL_PROFILES, copy_prepared_profiles_data
from clive_local_tools.testnet_block_log import ALT_WORKING_ACCOUNT1_NAME, WATCHED_ACCOUNTS_NAMES

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


@pytest.fixture(autouse=True)
def _prepare_data() -> None:
    copy_prepared_profiles_data(safe_settings.data_path)


OTHER_ACCOUNT: Final[str] = WATCHED_ACCOUNTS_NAMES[0]


async def test_unlock_old_profile(cli_tester_locked: CLITester) -> None:
    # ACT
    result = cli_tester_locked.unlock(
        profile_name=ALT_WORKING_ACCOUNT1_NAME, password_stdin=ALT_WORKING_ACCOUNT1_NAME * 2
    )

    # ASSERT
    assert_no_exit_code_error(result)


async def test_load_migrated_profile(cli_tester_locked: CLITester) -> None:
    # ARRANGE
    cli_tester_locked.unlock(profile_name=ALT_WORKING_ACCOUNT1_NAME, password_stdin=ALT_WORKING_ACCOUNT1_NAME * 2)
    cli_tester = cli_tester_locked

    # ACT & ASSERT
    result = cli_tester.show_profile()
    assert_no_exit_code_error(result)
    assert f"Profile name: {ALT_WORKING_ACCOUNT1_NAME}" in result.output, "profile is not loaded"


async def test_load_migrated_profile_with_transaction(cli_tester_locked: CLITester) -> None:
    # ARRANGE
    cli_tester_locked.unlock(profile_name=ALT_WORKING_ACCOUNT1_NAME, password_stdin=ALT_WORKING_ACCOUNT1_NAME * 2)
    cli_tester = cli_tester_locked

    # ACT & ASSERT
    result = cli_tester.show_profile()
    assert_no_exit_code_error(result)
    assert f"Profile name: {ALT_WORKING_ACCOUNT1_NAME}" in result.output, "profile is not loaded"


async def test_save_changes_in_migrated_profile(cli_tester_locked: CLITester) -> None:
    # ARRANGE
    cli_tester_locked.unlock(profile_name=ALT_WORKING_ACCOUNT1_NAME, password_stdin=ALT_WORKING_ACCOUNT1_NAME * 2)
    cli_tester = cli_tester_locked

    # ACT & ASSERT
    result = cli_tester.configure_tracked_account_add(account_name=OTHER_ACCOUNT)
    assert_no_exit_code_error(result)
    result = cli_tester.show_profile()
    assert OTHER_ACCOUNT in result.output, f"{OTHER_ACCOUNT} should be added to tracked accounts"

    result = cli_tester.configure_tracked_account_remove(account_name=OTHER_ACCOUNT)
    assert_no_exit_code_error(result)
    result = cli_tester.show_profile()
    assert OTHER_ACCOUNT in result.output, f"{OTHER_ACCOUNT} should be removed from tracked accounts"


async def test_unlock_uses_newest_version_of_profile(cli_tester_locked: CLITester) -> None:
    # ARRANGE
    cli_tester_locked.unlock(profile_name=ALT_WORKING_ACCOUNT1_NAME, password_stdin=ALT_WORKING_ACCOUNT1_NAME * 2)
    cli_tester = cli_tester_locked
    cli_tester.configure_tracked_account_add(account_name=OTHER_ACCOUNT)

    # ACT & ASSERT
    cli_tester_locked.lock()
    cli_tester_locked.unlock(profile_name=ALT_WORKING_ACCOUNT1_NAME, password_stdin=ALT_WORKING_ACCOUNT1_NAME * 2)

    result = cli_tester.configure_tracked_account_remove(account_name=OTHER_ACCOUNT)
    assert_no_exit_code_error(result)
    result = cli_tester.show_profile()
    assert OTHER_ACCOUNT in result.output, f"{OTHER_ACCOUNT} should be removed from tracked accounts"


async def test_show_profiles_includes_version_info(cli_tester_locked: CLITester) -> None:
    # ACT & ASSERT
    result = cli_tester_locked.show_profiles()
    assert_no_exit_code_error(result)
    for profile_name in ALL_PROFILES:
        assert profile_name in result.output, f"Profile {profile_name} should be listed"
