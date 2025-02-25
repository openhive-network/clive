from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive_local_tools.cli.checkers import assert_show_balances_title
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_NAMES

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

ANY_ACCOUNT_NAME_IN_BLOCKCHAIN: Final[str] = WATCHED_ACCOUNTS_NAMES[0]
ANY_OTHER_ACCOUNT_NAME_IN_BLOCKCHAIN: Final[str] = WATCHED_ACCOUNTS_NAMES[1]


def test_positional_have_default_value(cli_tester: CLITester) -> None:
    # ARRANGE
    profile = cli_tester.world.profile
    working_account_name_default = profile.accounts.working.name

    # ACT & ASSERT
    assert_show_balances_title(cli_tester, working_account_name_default)


def test_explicit_positional_takes_precedence_over_default(cli_tester: CLITester) -> None:
    # ARRANGE
    account_name_positional_value = ANY_ACCOUNT_NAME_IN_BLOCKCHAIN

    # ACT
    result = cli_tester.invoke_raw_command(["show", "balances", account_name_positional_value])

    # ASSERT
    assert_show_balances_title(result, account_name_positional_value)


@pytest.mark.parametrize(
    "account_name_positional_value",
    [None, ANY_OTHER_ACCOUNT_NAME_IN_BLOCKCHAIN],
    ids=["over default", "over positional"],
)
def test_explicit_option_takes_precedence(account_name_positional_value: str | None, cli_tester: CLITester) -> None:
    # ARRANGE
    account_name_option_value = ANY_ACCOUNT_NAME_IN_BLOCKCHAIN
    command = ["show", "balances"]

    if account_name_positional_value is not None:
        command += [account_name_positional_value]
    command += [f"--account-name={account_name_option_value}"]

    # ACT
    result = cli_tester.invoke_raw_command(command)

    # ASSERT
    assert_show_balances_title(result, account_name_option_value)


def test_option_placed_before_positional_takes_precedence(cli_tester: CLITester) -> None:
    # ARRANGE
    account_name_positional_value = ANY_ACCOUNT_NAME_IN_BLOCKCHAIN
    account_name_option_value = ANY_OTHER_ACCOUNT_NAME_IN_BLOCKCHAIN

    # ACT
    result = cli_tester.invoke_raw_command(
        ["show", "balances", f"--account-name={account_name_option_value}", account_name_positional_value]
    )

    # ASSERT
    assert_show_balances_title(result, account_name_option_value)
