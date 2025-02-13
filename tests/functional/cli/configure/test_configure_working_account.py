from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.core.encryption import EncryptionService
from clive_local_tools.checkers.profile_accounts_checker import ProfileAccountsChecker
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_NAMES, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


async def test_configure_working_account_switch(cli_tester: CLITester) -> None:
    """Check clive configure working-account switch command."""
    # ARRANGE
    profile_name = cli_tester.world.profile.name
    encryption_service = EncryptionService(
        cli_tester.world._unlocked_wallets_ensure.blockchain_keys,
        cli_tester.world._unlocked_wallets_ensure.profile_encryption,
    )
    profile_account_checker = ProfileAccountsChecker(profile_name, encryption_service)
    account_to_switch = WATCHED_ACCOUNTS_NAMES[0]

    # ACT
    await profile_account_checker.assert_working_account(working_account=WORKING_ACCOUNT_NAME)
    await profile_account_checker.assert_in_tracked_accounts(account_names=[account_to_switch])

    cli_tester.configure_working_account_switch(account_name=account_to_switch)

    # ASSERT
    await profile_account_checker.assert_working_account(working_account=account_to_switch)
    await profile_account_checker.assert_in_tracked_accounts(account_names=[account_to_switch])


async def test_configure_working_account_switch_same_account(cli_tester: CLITester) -> None:
    """Check clive configure working-account switch to already selected account."""
    # ARRANGE
    message = f"Account {WORKING_ACCOUNT_NAME} is already a working account."

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.configure_working_account_switch(account_name=WORKING_ACCOUNT_NAME)


async def test_configure_working_account_switch_to_not_existing_account(cli_tester: CLITester) -> None:
    """Check clive configure working-account switch to not existing account."""
    # ARRANGE
    account_not_exists = "bobo"
    message = f"Account {account_not_exists} not found."

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.configure_working_account_switch(account_name=account_not_exists)
