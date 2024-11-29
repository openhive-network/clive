from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.core.profile import Profile
from clive_local_tools.checkers import assert_wallet_unlocked, assert_wallets_locked
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import (
    ALT_WORKING_ACCOUNT1_PASSWORD,
    WORKING_ACCOUNT_PASSWORD,
)
from clive_local_tools.testnet_block_log import (
    ALT_WORKING_ACCOUNT1_NAME,
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import Beekeeper
    from clive_local_tools.cli.cli_tester import CLITester


MESSAGE_NO_SESSION_TOKEN: Final[str] = "Beekeeper session token is not set"


@pytest.fixture
async def prepare_second_profile() -> Profile:
    profile = Profile.create(ALT_WORKING_ACCOUNT1_NAME)
    profile.save()
    return profile


@pytest.fixture
async def prepare_second_beekeeper_wallet(
    beekeeper: Beekeeper,
    prepare_second_profile: Profile,  # noqa: ARG001
) -> None:
    wallet_name = ALT_WORKING_ACCOUNT1_NAME
    await beekeeper.api.create(wallet_name=wallet_name, password=ALT_WORKING_ACCOUNT1_PASSWORD)
    await beekeeper.api.lock(wallet_name=wallet_name)


async def test_lock(beekeeper: Beekeeper, cli_tester_with_session_token_unlocked: CLITester) -> None:
    # ACT
    cli_tester_with_session_token_unlocked.lock()

    # ASSERT
    await assert_wallets_locked(beekeeper)


async def test_unlock_one_profile(beekeeper: Beekeeper, cli_tester_with_session_token_locked: CLITester) -> None:
    # ACT
    cli_tester_with_session_token_locked.unlock(
        profile_name=WORKING_ACCOUNT_NAME, password_stdin=WORKING_ACCOUNT_PASSWORD
    )

    # ASSERT
    await assert_wallet_unlocked(beekeeper, WORKING_ACCOUNT_NAME)


async def test_negative_unlocking_single_profile_when_multiple_profiles_exist(
    cli_tester_with_session_token_locked: CLITester,
    prepare_second_beekeeper_wallet: None,  # noqa: ARG001
) -> None:
    # ARRANGE
    message = "All wallets in session should be locked."
    cli_tester_with_session_token_locked.unlock(
        profile_name=ALT_WORKING_ACCOUNT1_NAME, password_stdin=ALT_WORKING_ACCOUNT1_PASSWORD
    )

    # ACT
    # ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester_with_session_token_locked.unlock(
            profile_name=ALT_WORKING_ACCOUNT1_NAME, password_stdin=ALT_WORKING_ACCOUNT1_PASSWORD
        )


async def test_negative_unlock_profile_name_invalid(cli_tester_with_session_token_locked: CLITester) -> None:
    # ARRANGE
    invalid_profile_name = "invalid-profile-name"
    message = f"Profile `{invalid_profile_name}` does not exist."

    # ACT
    # ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester_with_session_token_locked.unlock(
            profile_name=invalid_profile_name, password_stdin=WORKING_ACCOUNT_PASSWORD
        )


async def test_negative_unlock_password_invalid(cli_tester_with_session_token_locked: CLITester) -> None:
    # ARRANGE
    invalid_password = "invalid-password"
    message = f"Password for profile `{WORKING_ACCOUNT_NAME}` is incorrect."

    # ACT
    # ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester_with_session_token_locked.unlock(profile_name=WORKING_ACCOUNT_NAME, password_stdin=invalid_password)


async def test_negative_unlock_already_unlocked(cli_tester_with_session_token_unlocked: CLITester) -> None:
    # ARRANGE
    message = "All wallets in session should be locked."

    # ACT
    # ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester_with_session_token_unlocked.unlock()


async def test_negative_lock_without_session_token(cli_tester: CLITester) -> None:
    # ACT
    # ASSERT
    with pytest.raises(CLITestCommandError, match=MESSAGE_NO_SESSION_TOKEN):
        cli_tester.lock()


async def test_negative_unlock_without_session_token(cli_tester: CLITester) -> None:
    # ACT
    # ASSERT
    with pytest.raises(CLITestCommandError, match=MESSAGE_NO_SESSION_TOKEN):
        cli_tester.unlock(profile_name=WORKING_ACCOUNT_NAME, password_stdin=WORKING_ACCOUNT_PASSWORD)
