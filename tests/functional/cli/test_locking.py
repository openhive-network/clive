from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.cli.exceptions import CLIBeekeeperRemoteAddressIsNotSetError, CLIBeekeeperSessionTokenNotSetError
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.world import World
from clive_local_tools.checkers.wallet_checkers import assert_wallet_unlocked, assert_wallets_locked
from clive_local_tools.cli.checkers import assert_unlocked_profile
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import (
    ALT_WORKING_ACCOUNT1_KEY_ALIAS,
    ALT_WORKING_ACCOUNT1_PASSWORD,
    WORKING_ACCOUNT_PASSWORD,
)
from clive_local_tools.testnet_block_log import (
    ALT_WORKING_ACCOUNT1_DATA,
    ALT_WORKING_ACCOUNT1_NAME,
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from clive_local_tools.cli.cli_tester import CLITester
    from clive_local_tools.types import EnvContextFactory


@pytest.fixture
async def cli_tester_locked_with_second_profile(cli_tester_locked: CLITester) -> CLITester:
    async with World() as world_cm:
        await world_cm.create_new_profile_with_wallets(ALT_WORKING_ACCOUNT1_NAME, ALT_WORKING_ACCOUNT1_PASSWORD)
        world_cm.profile.keys.add_to_import(
            PrivateKeyAliased(
                value=ALT_WORKING_ACCOUNT1_DATA.account.private_key, alias=f"{ALT_WORKING_ACCOUNT1_KEY_ALIAS}"
            )
        )
        await world_cm.commands.sync_data_with_beekeeper()
        await world_cm.commands.save_profile()  # required for saving imported keys aliases
        await world_cm.commands.lock()
        world_cm.profile.skip_saving()  # cannot save profile when it is locked because encryption is not possible
    return cli_tester_locked


@pytest.fixture
async def cli_tester_without_remote_address(
    beekeeper_remote_address_env_context_factory: EnvContextFactory,
    cli_tester: CLITester,
) -> AsyncGenerator[CLITester]:
    with beekeeper_remote_address_env_context_factory(None):
        yield cli_tester


async def test_negative_lock_without_remote_address(cli_tester_without_remote_address: CLITester) -> None:
    # ARRANGE

    # ACT
    # ASSERT
    with pytest.raises(CLITestCommandError, match=CLIBeekeeperRemoteAddressIsNotSetError.MESSAGE):
        cli_tester_without_remote_address.lock()


async def test_negative_unlock_without_remote_address(cli_tester_without_remote_address: CLITester) -> None:
    # ARRANGE

    # ACT
    # ASSERT
    with pytest.raises(CLITestCommandError, match=CLIBeekeeperRemoteAddressIsNotSetError.MESSAGE):
        cli_tester_without_remote_address.unlock(
            profile_name=WORKING_ACCOUNT_NAME, password_stdin=WORKING_ACCOUNT_PASSWORD
        )


async def test_lock(cli_tester: CLITester) -> None:
    # ACT
    cli_tester.lock()
    cli_tester.world.profile.skip_saving()  # cannot save profile when it is locked because encryption is not possible

    # ASSERT
    await assert_wallets_locked(cli_tester.world.beekeeper_manager.beekeeper)


async def test_unlock_one_profile(cli_tester_locked: CLITester) -> None:
    # ACT
    cli_tester_locked.unlock(profile_name=WORKING_ACCOUNT_NAME, password_stdin=WORKING_ACCOUNT_PASSWORD)

    # ASSERT
    await assert_wallet_unlocked(cli_tester_locked.world.beekeeper_manager.beekeeper, WORKING_ACCOUNT_NAME)


async def test_second_profile(cli_tester_locked_with_second_profile: CLITester) -> None:
    # ARRANGE
    cli_tester = cli_tester_locked_with_second_profile

    # ACT
    cli_tester.unlock(profile_name=ALT_WORKING_ACCOUNT1_NAME, password_stdin=ALT_WORKING_ACCOUNT1_PASSWORD)
    assert_unlocked_profile(cli_tester, ALT_WORKING_ACCOUNT1_NAME)

    cli_tester.lock()
    cli_tester.unlock(profile_name=WORKING_ACCOUNT_NAME, password_stdin=WORKING_ACCOUNT_PASSWORD)

    # ASSERT
    assert_unlocked_profile(cli_tester, WORKING_ACCOUNT_NAME)


async def test_negative_unlock_profile_name_invalid(cli_tester_locked: CLITester) -> None:
    # ARRANGE
    invalid_profile_name = "invalid-profile-name"
    message = f"Profile `{invalid_profile_name}` does not exist."

    # ACT
    # ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester_locked.unlock(profile_name=invalid_profile_name, password_stdin=WORKING_ACCOUNT_PASSWORD)


async def test_negative_unlock_password_invalid(cli_tester_locked: CLITester) -> None:
    # ARRANGE
    invalid_password = "invalid-password"
    message = f"Password for profile `{WORKING_ACCOUNT_NAME}` is incorrect."

    # ACT
    # ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester_locked.unlock(profile_name=WORKING_ACCOUNT_NAME, password_stdin=invalid_password)


async def test_negative_unlock_already_unlocked(cli_tester: CLITester) -> None:
    # ARRANGE
    message = "All wallets in session should be locked."

    # ACT
    # ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.unlock()


async def test_negative_lock_without_session_token(cli_tester_without_session_token: CLITester) -> None:
    # ACT
    # ASSERT
    with pytest.raises(CLITestCommandError, match=CLIBeekeeperSessionTokenNotSetError.MESSAGE):
        cli_tester_without_session_token.lock()


async def test_negative_unlock_without_session_token(cli_tester_without_session_token: CLITester) -> None:
    # ACT
    # ASSERT
    with pytest.raises(CLITestCommandError, match=CLIBeekeeperSessionTokenNotSetError.MESSAGE):
        cli_tester_without_session_token.unlock(
            profile_name=WORKING_ACCOUNT_NAME,
            password_stdin=WORKING_ACCOUNT_PASSWORD,
        )
