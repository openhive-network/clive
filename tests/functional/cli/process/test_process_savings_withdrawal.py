from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import test_tools as tt

from clive_local_tools.cli import checkers
from clive_local_tools.cli.exceptions import CliveCommandError
from clive_local_tools.data.constants import (
    WORKING_ACCOUNT,
    WORKING_ACCOUNT_HBD_LIQUID_BALANCE,
    WORKING_ACCOUNT_HIVE_LIQUID_BALANCE,
    WORKING_ACCOUNT_KEY_ALIAS,
)

if TYPE_CHECKING:
    from clive_local_tools.cli.testing_cli import TestingCli


amount_to_deposit_hbd = tt.Asset.Hbd(0.238)
amount_to_deposit_hive = tt.Asset.Test(0.236)
large_amount = tt.Asset.Test(234234.236)
deposit_memo = "memo1"
withdrawal_memo = "memo2"


@pytest.mark.parametrize(
    ("amount_to_deposit", "working_account_balance"),
    [
        (amount_to_deposit_hive, WORKING_ACCOUNT_HIVE_LIQUID_BALANCE),
        (amount_to_deposit_hbd, WORKING_ACCOUNT_HBD_LIQUID_BALANCE),
    ],
    ids=["hive", "hbd"],
)
async def test_withdrawal_valid(
    testing_cli: TestingCli,
    amount_to_deposit: tt.Asset.AnyT,
    working_account_balance: tt.Asset.AnyT,
) -> None:
    # ARRANGE
    testing_cli.process_savings_deposit(
        amount=amount_to_deposit.as_legacy(), password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ACT
    testing_cli.process_savings_withdrawal(
        amount=amount_to_deposit.as_legacy(), password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT
    checkers.assert_balances(
        testing_cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=tt.Asset.Hive(0),
        balance="Savings",
    )
    checkers.assert_balances(
        testing_cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=working_account_balance - amount_to_deposit.amount,
        balance="Liquid",
    )


async def test_withdrawal_invalid(testing_cli: TestingCli) -> None:
    # ACT
    with pytest.raises(CliveCommandError) as withdrawal_exception_info:
        testing_cli.process_savings_withdrawal(
            amount=large_amount.as_legacy(), password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
        )
    withdrawal_error = withdrawal_exception_info.value
    assert withdrawal_error.exit_code == 1

    # ASSERT
    checkers.assert_balances(
        testing_cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=tt.Asset.Hive(0),
        balance="Savings",
    )
    checkers.assert_balances(
        testing_cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=WORKING_ACCOUNT_HIVE_LIQUID_BALANCE,
        balance="Liquid",
    )


async def test_withdrawal_with_memo(testing_cli: TestingCli) -> None:
    # ARRANGE
    testing_cli.process_savings_deposit(
        amount=amount_to_deposit_hive.as_legacy(),
        memo=deposit_memo,
        password=WORKING_ACCOUNT.name,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ACT
    testing_cli.process_savings_withdrawal(
        amount=amount_to_deposit_hive.as_legacy(),
        memo=withdrawal_memo,
        password=WORKING_ACCOUNT.name,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    checkers.assert_balances(
        testing_cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=tt.Asset.Hive(0),
        balance="Savings",
    )
    checkers.assert_balances(
        testing_cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=WORKING_ACCOUNT_HIVE_LIQUID_BALANCE - amount_to_deposit_hive.amount,
        balance="Liquid",
    )
    result = testing_cli.show_pending_withdrawals()
    assert withdrawal_memo in result.output
