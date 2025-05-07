from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.cli.exceptions import CLINoProfileUnlockedError
from clive_local_tools.cli.checkers import assert_unlocked_profile
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log import ALT_WORKING_ACCOUNT1_NAME, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


async def test_remove_profile_when_locked(cli_tester_locked: CLITester) -> None:
    # ARRANGE & ACT
    cli_tester_locked.configure_profile_delete(profile_name=WORKING_ACCOUNT_NAME)

    # ASSERT
    result = cli_tester_locked.show_profiles()
    assert WORKING_ACCOUNT_NAME not in result.output, f"Profile {WORKING_ACCOUNT_NAME} should be deleted"


async def test_remove_currently_unlocked_profile(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.world.profile.skip_saving()

    # ACT
    cli_tester.configure_profile_delete(profile_name=WORKING_ACCOUNT_NAME)

    # ASSERT
    with pytest.raises(CLITestCommandError, match=CLINoProfileUnlockedError.MESSAGE):
        cli_tester.show_profile()


async def test_remove_other_profile_when_unlocked(cli_tester_locked_with_second_profile: CLITester) -> None:
    # ARRANGE
    cli_tester = cli_tester_locked_with_second_profile
    cli_tester.unlock(profile_name=WORKING_ACCOUNT_NAME, password_stdin=WORKING_ACCOUNT_PASSWORD)

    # ACT
    cli_tester_locked_with_second_profile.configure_profile_delete(profile_name=ALT_WORKING_ACCOUNT1_NAME)

    # ASSERT
    assert_unlocked_profile(cli_tester, WORKING_ACCOUNT_NAME)


async def test_remove_profile_beekeeper_not_set(cli_tester_without_remote_address: CLITester) -> None:
    # ARRANGE & ACT
    cli_tester_without_remote_address.configure_profile_delete(profile_name=WORKING_ACCOUNT_NAME)

    # ASSERT
    result = cli_tester_without_remote_address.show_profiles()
    assert WORKING_ACCOUNT_NAME not in result.output, f"Profile {WORKING_ACCOUNT_NAME} should be deleted"
