from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive_local_tools.cli import checkers
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log import WORKING_ACCOUNT_DATA

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
        (AMOUNT_TO_DEPOSIT_HIVE, WORKING_ACCOUNT_DATA.hives_liquid),
        (AMOUNT_TO_DEPOSIT_HBD, WORKING_ACCOUNT_DATA.hbds_liquid),
    ],
    ids=["hive", "hbd"],
)
async def test_withdrawal_valid(
    cli_tester: CLITester,
    amount_to_deposit: tt.Asset.AnyT,
    working_account_balance: tt.Asset.AnyT,
) -> None:
    # ARRANGE
    cli_tester.process_savings_deposit(amount=amount_to_deposit, sign_with=WORKING_ACCOUNT_KEY_ALIAS)

    # ACT
    cli_tester.process_savings_withdrawal(amount=amount_to_deposit, sign_with=WORKING_ACCOUNT_KEY_ALIAS)

    # ASSERT
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT_DATA.account.name,
        asset_amount=tt.Asset.Hive(0),
        balance="Savings",
    )
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT_DATA.account.name,
        asset_amount=working_account_balance - amount_to_deposit,
        balance="Liquid",
    )


async def test_withdrawal_invalid(cli_tester: CLITester) -> None:
    # ARRANGE
    expected_error = "Assert Exception:_db.get_savings_balance"

    # ACT
    with pytest.raises(CLITestCommandError, match=expected_error) as withdrawal_exception_info:
        cli_tester.process_savings_withdrawal(amount=LARGE_AMOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
    checkers.assert_exit_code(withdrawal_exception_info, 1)

    # ASSERT
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT_DATA.account.name,
        asset_amount=tt.Asset.Hive(0),
        balance="Savings",
    )
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT_DATA.account.name,
        asset_amount=WORKING_ACCOUNT_DATA.hives_liquid,
        balance="Liquid",
    )


async def test_withdrawal_with_memo(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_savings_deposit(
        amount=AMOUNT_TO_DEPOSIT_HIVE, memo=DEPOSIT_MEMO, sign_with=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ACT
    cli_tester.process_savings_withdrawal(
        amount=AMOUNT_TO_DEPOSIT_HIVE, memo=WITHDRAWAL_MEMO, sign_with=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT_DATA.account.name,
        asset_amount=tt.Asset.Hive(0),
        balance="Savings",
    )
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT_DATA.account.name,
        asset_amount=WORKING_ACCOUNT_DATA.hives_liquid - AMOUNT_TO_DEPOSIT_HIVE,
        balance="Liquid",
    )
    result = cli_tester.show_pending_withdrawals()
    assert WITHDRAWAL_MEMO in result.output, f"There should be memo `{WITHDRAWAL_MEMO}` in transaction."
