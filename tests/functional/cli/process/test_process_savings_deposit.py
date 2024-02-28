from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive_local_tools.cli import checkers
from clive_local_tools.cli.exceptions import CliveCommandError
from clive_local_tools.data.constants import (
    WATCHED_ACCOUNTS,
    WORKING_ACCOUNT,
    WORKING_ACCOUNT_HBD_LIQUID_BALANCE,
    WORKING_ACCOUNT_HIVE_LIQUID_BALANCE,
    WORKING_ACCOUNT_KEY_ALIAS,
)

if TYPE_CHECKING:
    from clive_local_tools.cli.testing_cli import TestingCli


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
    testing_cli: TestingCli,
    amount_to_deposit: tt.Asset.AnyT,
    working_account_balance: tt.Asset.AnyT,
) -> None:
    # ACT
    testing_cli.process_savings_deposit(
        amount=amount_to_deposit.as_legacy(), password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT
    checkers.assert_balances(
        testing_cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=amount_to_deposit,
        balance="Savings",
    )
    checkers.assert_balances(
        testing_cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=working_account_balance - amount_to_deposit.amount,
        balance="Liquid",
    )


async def test_deposit_to_other_account(testing_cli: TestingCli) -> None:
    # ARRANGE
    other_account = WATCHED_ACCOUNTS[0]

    # ACT
    testing_cli.process_savings_deposit(
        amount=AMOUNT_TO_DEPOSIT_HIVE.as_legacy(),
        to=other_account.name,
        password=WORKING_ACCOUNT.name,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        **{"from": WORKING_ACCOUNT.name},
    )

    # ASSERT
    checkers.assert_balances(
        testing_cli,
        account_name=f"{other_account.name}",
        asset_amount=AMOUNT_TO_DEPOSIT_HIVE,
        balance="Savings",
    )
    checkers.assert_balances(
        testing_cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=tt.Asset.Hive(0),
        balance="Savings",
    )
    checkers.assert_balances(
        testing_cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=WORKING_ACCOUNT_HIVE_LIQUID_BALANCE - AMOUNT_TO_DEPOSIT_HIVE.amount,
        balance="Liquid",
    )


async def test_deposit_not_enough_hive(testing_cli: TestingCli) -> None:
    # ACT
    with pytest.raises(CliveCommandError) as deposit_exception_info:
        testing_cli.process_savings_deposit(
            amount=LARGE_AMOUNT.as_legacy(), password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
        )
    deposit_error = deposit_exception_info.value
    assert deposit_error.exit_code == 1

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


async def test_deposit_with_memo(testing_cli: TestingCli) -> None:
    # ACT
    result = testing_cli.process_savings_deposit(
        amount=AMOUNT_TO_DEPOSIT_HIVE.as_legacy(),
        memo=DEPOSIT_MEMO,
        password=WORKING_ACCOUNT.name,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert DEPOSIT_MEMO in result.output
    checkers.assert_balances(
        testing_cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=AMOUNT_TO_DEPOSIT_HIVE,
        balance="Savings",
    )
    checkers.assert_balances(
        testing_cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=WORKING_ACCOUNT_HIVE_LIQUID_BALANCE - AMOUNT_TO_DEPOSIT_HIVE.amount,
        balance="Liquid",
    )
