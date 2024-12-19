from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive_local_tools.checkers.profile_accounts_checker import ProfileAccountsChecker
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.testnet_block_log.constants import (
    ALT_WORKING_ACCOUNT1_NAME,
    WATCHED_ACCOUNTS_NAMES,
)

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

ACCOUNT_TO_REMOVE: Final[str] = WATCHED_ACCOUNTS_NAMES[0]


async def test_configure_known_account_add(cli_tester: CLITester) -> None:
    """Check clive configure known-account add command."""
    # ARRANGE
    account_to_add = ALT_WORKING_ACCOUNT1_NAME
    profile_checker = ProfileAccountsChecker(cli_tester.world.profile.name, cli_tester.world.wallets._content)

    # ACT
    cli_tester.configure_known_account_add(account_name=account_to_add)

    # ASSERT
    await profile_checker.assert_in_known_accounts(account_names=[account_to_add])


async def test_configure_known_account_add_already_known_account(cli_tester: CLITester) -> None:
    """Check clive configure known-account add command with already known account."""
    # ARRANGE
    account_to_add = ALT_WORKING_ACCOUNT1_NAME
    message = "Can't add this account: This account is already known."
    cli_tester.configure_known_account_add(account_name=account_to_add)

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.configure_known_account_add(account_name=account_to_add)


async def test_configure_known_account_remove(cli_tester: CLITester) -> None:
    """Check clive configure known-account remove command."""
    # ARRANGE
    profile_checker = ProfileAccountsChecker(cli_tester.world.profile.name, cli_tester.world.wallets._content)
    cli_tester.configure_known_account_add(account_name=ACCOUNT_TO_REMOVE)
    await profile_checker.assert_in_known_accounts(account_names=[ACCOUNT_TO_REMOVE])

    # ACT
    cli_tester.configure_known_account_remove(account_name=ACCOUNT_TO_REMOVE)

    # ASSERT
    await profile_checker.assert_not_in_known_accounts(account_names=[ACCOUNT_TO_REMOVE])


async def test_configure_known_account_remove_not_known_account(cli_tester: CLITester) -> None:
    """Check clive configure known-account remove command on not known account."""
    # ARRANGE
    message = f"Known account {ACCOUNT_TO_REMOVE} not found."

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.configure_known_account_remove(account_name=ACCOUNT_TO_REMOVE)
