from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.core.encryption import EncryptionService
from clive_local_tools.checkers.profile_accounts_checker import ProfileAccountsChecker
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.testnet_block_log.constants import (
    ALT_WORKING_ACCOUNT1_NAME,
    WATCHED_ACCOUNTS_NAMES,
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

PROFILE_NAME: Final[str] = WORKING_ACCOUNT_NAME
ACCOUNT_TO_REMOVE: Final[str] = WATCHED_ACCOUNTS_NAMES[0]


async def test_configure_tracked_account_add(cli_tester: CLITester) -> None:
    """Check clive configure tracked-account add command."""
    # ARRANGE
    account_to_add = ALT_WORKING_ACCOUNT1_NAME
    profile_name = cli_tester.world.profile.name
    encryption_service = EncryptionService(cli_tester.world._unlocked_profile_encryption_wallet_ensure)
    profile_checker = await ProfileAccountsChecker.create_async(profile_name, encryption_service)

    # ACT
    cli_tester.configure_tracked_account_add(account_name=account_to_add)

    # ASSERT
    await profile_checker.reload()
    profile_checker.assert_in_tracked_accounts(account_names=[account_to_add])
    profile_checker.assert_in_known_accounts(account_names=[account_to_add])


async def test_configure_tracked_account_add_already_tracked_account(cli_tester: CLITester) -> None:
    """Check clive configure tracked-account add command with already tracked account."""
    # ARRANGE
    account_to_add = ALT_WORKING_ACCOUNT1_NAME
    message = "Can't use this account name: You cannot track account while its already tracked."

    # ACT
    cli_tester.configure_tracked_account_add(account_name=account_to_add)

    # ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.configure_tracked_account_add(account_name=account_to_add)


async def test_configure_tracked_account_remove(cli_tester: CLITester) -> None:
    """Check clive configure tracked-account remove command."""
    # ARRANGE
    profile_name = cli_tester.world.profile.name
    encryption_service = EncryptionService(cli_tester.world._unlocked_profile_encryption_wallet_ensure)
    profile_checker = await ProfileAccountsChecker.create_async(profile_name, encryption_service)

    # ACT
    profile_checker.assert_in_tracked_accounts(account_names=[ACCOUNT_TO_REMOVE])
    cli_tester.configure_tracked_account_remove(account_name=ACCOUNT_TO_REMOVE)

    # ASSERT
    await profile_checker.reload()
    profile_checker.assert_not_in_tracked_accounts(account_names=[ACCOUNT_TO_REMOVE])


async def test_configure_tracked_account_remove_with_already_removed_account(cli_tester: CLITester) -> None:
    """Check clive configure tracked-account remove command with already removed account."""
    # ARRANGE
    message = f"Account {ACCOUNT_TO_REMOVE} not found."
    profile_name = cli_tester.world.profile.name
    encryption_service = EncryptionService(cli_tester.world._unlocked_profile_encryption_wallet_ensure)
    profile_checker = await ProfileAccountsChecker.create_async(profile_name, encryption_service)

    # ACT
    profile_checker.assert_in_tracked_accounts(account_names=[ACCOUNT_TO_REMOVE])
    cli_tester.configure_tracked_account_remove(account_name=ACCOUNT_TO_REMOVE)

    # ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.configure_tracked_account_remove(account_name=ACCOUNT_TO_REMOVE)
