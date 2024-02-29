from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive_local_tools.cli import checkers
from clive_local_tools.cli.exceptions import CliveCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT, WORKING_ACCOUNT_KEY_ALIAS

if TYPE_CHECKING:
    from clive_local_tools.cli.testing_cli import TestingCli


AMOUNT_TO_DEPOSIT: Final[tt.Asset.TestT] = tt.Asset.Test(0.234)


async def test_withdrawal_cancel_valid(testing_cli: TestingCli) -> None:
    # ARRANGE
    request_id = 13

    testing_cli.process_savings_deposit(
        amount=AMOUNT_TO_DEPOSIT.as_legacy(), password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
    )
    testing_cli.process_savings_withdrawal(
        amount=AMOUNT_TO_DEPOSIT.as_legacy(),
        password=WORKING_ACCOUNT.name,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        **{"request-id": str(request_id)},
    )

    # ACT
    testing_cli.process_savings_withdrawal_cancel(
        password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS, **{"request-id": str(request_id)}
    )

    # ASSERT
    result = testing_cli.show_pending_withdrawals()
    assert str(AMOUNT_TO_DEPOSIT.amount) not in result.stdout


async def test_withdrawal_cancel_invalid(testing_cli: TestingCli) -> None:
    # ARRANGE
    actual_request_id = 23
    invalid_request_id = 24

    testing_cli.process_savings_deposit(
        amount=AMOUNT_TO_DEPOSIT.as_legacy(), password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    testing_cli.process_savings_withdrawal(
        amount=AMOUNT_TO_DEPOSIT.as_legacy(),
        password=WORKING_ACCOUNT.name,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        **{"request-id": str(actual_request_id)},
    )

    # ACT
    with pytest.raises(CliveCommandError) as withdrawal_cancel_exception_info:
        testing_cli.process_savings_withdrawal_cancel(
            password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS, **{"request-id": str(invalid_request_id)}
        )
    withdrawal_cancel_error = withdrawal_cancel_exception_info.value
    assert withdrawal_cancel_error.exit_code == 1

    # ASSERT
    checkers.assert_pending_withrawals(
        testing_cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=AMOUNT_TO_DEPOSIT,
    )
