from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive_local_tools.checkers.profile_accounts_checker import ProfileAccountsChecker
from clive_local_tools.cli.exceptions import CLITestCommandError

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

ACCOUNT: Final[str] = "null"


async def test_configure_known_account_add(cli_tester: CLITester) -> None:
    """Check clive configure known-account add command."""
    # ARRANGE
    profile_checker = ProfileAccountsChecker(cli_tester.world.profile.name, cli_tester.world.beekeeper_manager._content)

    # ACT
    cli_tester.configure_known_account_add(account_name=ACCOUNT)

    # ASSERT
    await profile_checker.assert_in_known_accounts(account_names=[ACCOUNT])


async def test_configure_known_account_add_already_known_account(cli_tester: CLITester) -> None:
    """Check clive configure known-account add command with already known account."""
    # ARRANGE
    message = "Can't add this account: This account is already known."
    cli_tester.configure_known_account_add(account_name=ACCOUNT)

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.configure_known_account_add(account_name=ACCOUNT)


async def test_configure_known_account_remove(cli_tester: CLITester) -> None:
    """Check clive configure known-account remove command."""
    # ARRANGE
    profile_checker = ProfileAccountsChecker(cli_tester.world.profile.name, cli_tester.world.beekeeper_manager._content)
    cli_tester.configure_known_account_add(account_name=ACCOUNT)
    await profile_checker.assert_in_known_accounts(account_names=[ACCOUNT])

    # ACT
    cli_tester.configure_known_account_remove(account_name=ACCOUNT)

    # ASSERT
    await profile_checker.assert_not_in_known_accounts(account_names=[ACCOUNT])


async def test_configure_known_account_remove_not_known_account(cli_tester: CLITester) -> None:
    """Check clive configure known-account remove command on not known account."""
    # ARRANGE
    message = f"Known account {ACCOUNT} not found."

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.configure_known_account_remove(account_name=ACCOUNT)


async def test_if_known_account_enable_is_set_by_default(cli_tester_locked: CLITester) -> None:
    # ARRANGE
    profile_name = "KnownAccountEnabled"
    cli_tester_locked.configure_profile_add(profile_name=profile_name, password_stdin=profile_name)
    await cli_tester_locked.world.load_profile_based_on_beekepeer()
    profile_checker = ProfileAccountsChecker(
        cli_tester_locked.world.profile.name, cli_tester_locked.world.beekeeper_manager._content
    )

    # ASSERT
    assert (await profile_checker.profile).should_enable_known_accounts, (
        "Known account attribute should be enabled by default."
    )


async def test_configure_enable_known_accounts(cli_tester: CLITester) -> None:
    # ARRANGE
    profile_checker = ProfileAccountsChecker(cli_tester.world.profile.name, cli_tester.world.beekeeper_manager._content)

    # ACT
    cli_tester.configure_known_account_enable()

    # ASSERT
    assert (await profile_checker.profile).should_enable_known_accounts, "Known account attribute should be enabled."


async def test_configure_disable_known_account_add(cli_tester: CLITester) -> None:
    # ARRANGE
    profile_checker = ProfileAccountsChecker(cli_tester.world.profile.name, cli_tester.world.beekeeper_manager._content)

    # ACT
    cli_tester.configure_known_account_disable()

    # ASSERT
    assert not (await profile_checker.profile).should_enable_known_accounts, (
        "Known account attribute should be disabled."
    )
