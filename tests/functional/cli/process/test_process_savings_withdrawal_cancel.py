from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive_local_tools.cli import checkers
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log import WORKING_ACCOUNT_DATA, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT_TO_DEPOSIT: Final[tt.Asset.TestT] = tt.Asset.Test(0.234)


async def test_withdrawal_cancel_valid(cli_tester: CLITester) -> None:
    # ARRANGE
    request_id = 13

    cli_tester.process_savings_deposit(amount=AMOUNT_TO_DEPOSIT, sign=WORKING_ACCOUNT_KEY_ALIAS)
    cli_tester.process_savings_withdrawal(
        amount=AMOUNT_TO_DEPOSIT, sign=WORKING_ACCOUNT_KEY_ALIAS, request_id=request_id
    )

    # ACT
    cli_tester.process_savings_withdrawal_cancel(sign=WORKING_ACCOUNT_KEY_ALIAS, request_id=request_id)

    # ASSERT
    result = cli_tester.show_pending_withdrawals()
    assert (
        str(AMOUNT_TO_DEPOSIT.amount) not in result.stdout
    ), f"Withdrawal {request_id} of {AMOUNT_TO_DEPOSIT.as_legacy()} should be canceled."


async def test_withdrawal_cancel_invalid(cli_tester: CLITester) -> None:
    # ARRANGE
    actual_request_id = 23
    invalid_request_id = 24

    cli_tester.process_savings_deposit(amount=AMOUNT_TO_DEPOSIT, sign=WORKING_ACCOUNT_KEY_ALIAS)

    cli_tester.process_savings_withdrawal(
        amount=AMOUNT_TO_DEPOSIT, sign=WORKING_ACCOUNT_KEY_ALIAS, request_id=actual_request_id
    )
    expected_error = (
        rf"Savings withdraw for `owner` {WORKING_ACCOUNT_NAME} and 'request_id' {invalid_request_id} doesn't exist."
    )

    # ACT
    with pytest.raises(CLITestCommandError, match=expected_error) as withdrawal_cancel_exception_info:
        cli_tester.process_savings_withdrawal_cancel(sign=WORKING_ACCOUNT_KEY_ALIAS, request_id=invalid_request_id)
    checkers.assert_exit_code(withdrawal_cancel_exception_info, 1)

    # ASSERT
    checkers.assert_pending_withrawals(
        cli_tester,
        account_name=WORKING_ACCOUNT_DATA.account.name,
        asset_amount=AMOUNT_TO_DEPOSIT,
    )
