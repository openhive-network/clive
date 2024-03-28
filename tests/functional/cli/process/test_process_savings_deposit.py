from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive_local_tools.cli import checkers
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import (
    WATCHED_ACCOUNTS,
    WORKING_ACCOUNT,
    WORKING_ACCOUNT_HBD_LIQUID_BALANCE,
    WORKING_ACCOUNT_HIVE_LIQUID_BALANCE,
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT_TO_DEPOSIT_HBD: Final[tt.Asset.HbdT] = tt.Asset.Hbd(0.237)
AMOUNT_TO_DEPOSIT_HIVE: Final[tt.Asset.HiveT] = tt.Asset.Test(0.235)
LARGE_AMOUNT: Final[tt.Asset.TestT] = tt.Asset.Test(234234.235)
DEPOSIT_MEMO: Final[str] = "memo0"


@pytest.mark.parametrize(
    ("amount_to_deposit", "working_account_balance"),
    [
        (AMOUNT_TO_DEPOSIT_HIVE, WORKING_ACCOUNT_HIVE_LIQUID_BALANCE),
        (AMOUNT_TO_DEPOSIT_HBD, WORKING_ACCOUNT_HBD_LIQUID_BALANCE),
    ],
    ids=["hive", "hbd"],
)
async def test_deposit_valid(
    cli_tester: CLITester,
    amount_to_deposit: tt.Asset.AnyT,
    working_account_balance: tt.Asset.AnyT,
) -> None:
    # ACT
    cli_tester.process_savings_deposit(
        amount=amount_to_deposit, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT.name,
        asset_amount=amount_to_deposit,
        balance="Savings",
    )
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT.name,
        asset_amount=working_account_balance - amount_to_deposit.amount,
        balance="Liquid",
    )


async def test_deposit_to_other_account(cli_tester: CLITester) -> None:
    # ARRANGE
    other_account = WATCHED_ACCOUNTS[0]

    # ACT
    cli_tester.process_savings_deposit(
        amount=AMOUNT_TO_DEPOSIT_HIVE,
        to=other_account.name,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        from_=WORKING_ACCOUNT.name,
    )

    # ASSERT
    checkers.assert_balances(
        cli_tester,
        account_name=other_account.name,
        asset_amount=AMOUNT_TO_DEPOSIT_HIVE,
        balance="Savings",
    )
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT.name,
        asset_amount=tt.Asset.Hive(0),
        balance="Savings",
    )
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT.name,
        asset_amount=WORKING_ACCOUNT_HIVE_LIQUID_BALANCE - AMOUNT_TO_DEPOSIT_HIVE.amount,
        balance="Liquid",
    )


async def test_deposit_not_enough_hive(cli_tester: CLITester) -> None:
    # ARRANGE
    expected_error = "Account alice does not have sufficient funds for balance adjustment"

    # ACT
    with pytest.raises(CLITestCommandError, match=expected_error) as deposit_exception_info:
        cli_tester.process_savings_deposit(
            amount=LARGE_AMOUNT, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
        )
    checkers.assert_exit_code(deposit_exception_info, 1)

    # ASSERT
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT.name,
        asset_amount=tt.Asset.Hive(0),
        balance="Savings",
    )
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT.name,
        asset_amount=WORKING_ACCOUNT_HIVE_LIQUID_BALANCE,
        balance="Liquid",
    )


async def test_deposit_with_memo(cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.process_savings_deposit(
        amount=AMOUNT_TO_DEPOSIT_HIVE,
        memo=DEPOSIT_MEMO,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert DEPOSIT_MEMO in result.output, f"There should be memo `{DEPOSIT_MEMO}` in transaction."
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT.name,
        asset_amount=AMOUNT_TO_DEPOSIT_HIVE,
        balance="Savings",
    )
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT.name,
        asset_amount=WORKING_ACCOUNT_HIVE_LIQUID_BALANCE - AMOUNT_TO_DEPOSIT_HIVE.amount,
        balance="Liquid",
    )