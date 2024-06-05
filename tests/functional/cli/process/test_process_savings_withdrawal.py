from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive_local_tools.cli import checkers
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import (
    WORKING_ACCOUNT,
    WORKING_ACCOUNT_HBD_LIQUID_BALANCE,
    WORKING_ACCOUNT_HIVE_LIQUID_BALANCE,
)

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT_TO_DEPOSIT_HBD: Final[tt.Asset.HbdT] = tt.Asset.Hbd(0.238)
AMOUNT_TO_DEPOSIT_HIVE: Final[tt.Asset.HiveT] = tt.Asset.Test(0.236)
LARGE_AMOUNT: Final[tt.Asset.TestT] = tt.Asset.Test(234234.236)
DEPOSIT_MEMO: Final[str] = "memo1"
WITHDRAWAL_MEMO: Final[str] = "memo2"


@pytest.mark.parametrize(
    ("amount_to_deposit", "working_account_balance"),
    [
        (AMOUNT_TO_DEPOSIT_HIVE, WORKING_ACCOUNT_HIVE_LIQUID_BALANCE),
        (AMOUNT_TO_DEPOSIT_HBD, WORKING_ACCOUNT_HBD_LIQUID_BALANCE),
    ],
    ids=["hive", "hbd"],
)
async def test_withdrawal_valid(
    cli_tester: CLITester,
    amount_to_deposit: tt.Asset.AnyT,
    working_account_balance: tt.Asset.AnyT,
) -> None:
    # ARRANGE
    cli_tester.process_savings_deposit(
        amount=amount_to_deposit, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ACT
    cli_tester.process_savings_withdrawal(
        amount=amount_to_deposit, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

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
        asset_amount=working_account_balance - amount_to_deposit.amount,
        balance="Liquid",
    )


async def test_withdrawal_invalid(cli_tester: CLITester) -> None:
    # ARRANGE
    expected_error = "network_broadcast_api.broadcast_transaction"

    # ACT
    with pytest.raises(CLITestCommandError, match=expected_error) as withdrawal_exception_info:
        cli_tester.process_savings_withdrawal(
            amount=LARGE_AMOUNT, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
        )
    checkers.assert_exit_code(withdrawal_exception_info, 1)

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


async def test_withdrawal_with_memo(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_savings_deposit(
        amount=AMOUNT_TO_DEPOSIT_HIVE,
        memo=DEPOSIT_MEMO,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ACT
    cli_tester.process_savings_withdrawal(
        amount=AMOUNT_TO_DEPOSIT_HIVE,
        memo=WITHDRAWAL_MEMO,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

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
        asset_amount=WORKING_ACCOUNT_HIVE_LIQUID_BALANCE - AMOUNT_TO_DEPOSIT_HIVE.amount,
        balance="Liquid",
    )
    result = cli_tester.show_pending_withdrawals()
    assert WITHDRAWAL_MEMO in result.output, f"There should be memo `{WITHDRAWAL_MEMO}` in transaction."
