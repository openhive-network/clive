from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.checkers.profile_checker import ProfileChecker
from clive_local_tools.cli.checkers import assert_locked_profile, assert_unlocked_profile
from clive_local_tools.data.constants import WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log import ALT_WORKING_ACCOUNT1_NAME, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


async def test_remove_profile_when_locked(cli_tester_locked: CLITester) -> None:
    # ACT
    cli_tester_locked.configure_profile_delete(profile_name=WORKING_ACCOUNT_NAME)

    # ASSERT
    ProfileChecker.assert_profile_is_stored(WORKING_ACCOUNT_NAME, should_be_stored=False)


async def test_remove_currently_unlocked_profile(cli_tester: CLITester) -> None:
    # ARRANGE
    # profile would be saved in world_cm fixture but after deletion it is locked and saving gives errors
    cli_tester.world.profile.skip_saving()

    # ACT
    cli_tester.configure_profile_delete(profile_name=WORKING_ACCOUNT_NAME)

    # ASSERT
    ProfileChecker.assert_profile_is_stored(WORKING_ACCOUNT_NAME, should_be_stored=False)
    assert_locked_profile(cli_tester)


async def test_remove_other_profile_when_unlocked(cli_tester_locked_with_second_profile: CLITester) -> None:
    # ARRANGE
    cli_tester = cli_tester_locked_with_second_profile
    cli_tester.unlock(profile_name=WORKING_ACCOUNT_NAME, password_stdin=WORKING_ACCOUNT_PASSWORD)

    # ACT
    cli_tester.configure_profile_delete(profile_name=ALT_WORKING_ACCOUNT1_NAME)

    # ASSERT
    ProfileChecker.assert_profile_is_stored(ALT_WORKING_ACCOUNT1_NAME, should_be_stored=False)
    assert_unlocked_profile(cli_tester, WORKING_ACCOUNT_NAME)


async def test_remove_profile_session_token_not_set(cli_tester_without_session_token: CLITester) -> None:
    # ACT
    cli_tester_without_session_token.configure_profile_delete(profile_name=WORKING_ACCOUNT_NAME)

    # ASSERT
    ProfileChecker.assert_profile_is_stored(WORKING_ACCOUNT_NAME, should_be_stored=False)
