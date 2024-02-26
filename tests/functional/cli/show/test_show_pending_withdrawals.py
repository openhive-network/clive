from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt

from clive_local_tools.cli import checkers
from clive_local_tools.data.constants import WORKING_ACCOUNT, WORKING_ACCOUNT_KEY_ALIAS

if TYPE_CHECKING:
    from clive_local_tools.cli.testing_cli import TestingCli


amount_to_withdraw = tt.Asset.Test(0.111)
amount_to_withdraw2 = tt.Asset.Test(0.112)
amount_to_deposit = tt.Asset.Test(0.345)


async def test_show_pending_withdrawals_none(
    testing_cli: TestingCli,
) -> None:
    # ACT
    result = testing_cli.show_pending_withdrawals()

    # ASSERT
    assert "no pending withdrawals" in result.stdout


async def test_show_pending_withdrawals_basic(
    testing_cli: TestingCli,
) -> None:
    # ARRANGE
    testing_cli.process_savings_deposit(
        amount=amount_to_deposit.as_legacy(), password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    testing_cli.process_savings_withdrawal(
        amount=amount_to_withdraw.as_legacy(), password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    testing_cli.process_savings_withdrawal(
        amount=amount_to_withdraw2.as_legacy(), password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ACT
    # ASSERT
    checkers.assert_pending_withrawals(
        testing_cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=amount_to_withdraw,
    )
    checkers.assert_pending_withrawals(
        testing_cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=amount_to_withdraw2,
    )
