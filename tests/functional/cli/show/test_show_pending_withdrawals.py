from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive_local_tools.cli import checkers
from clive_local_tools.data.constants import WORKING_ACCOUNT, WORKING_ACCOUNT_KEY_ALIAS

if TYPE_CHECKING:
    from clive_local_tools.cli.testing_cli import TestingCli


AMOUNT_TO_WITHDRAW: Final[tt.Asset.TestT] = tt.Asset.Test(0.111)
AMOUNT_TO_WITHDRAW2: Final[tt.Asset.TestT] = tt.Asset.Test(0.112)
AMOUNT_TO_DEPOSIT: Final[tt.Asset.TestT] = tt.Asset.Test(0.345)


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
        amount=AMOUNT_TO_DEPOSIT, password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    testing_cli.process_savings_withdrawal(
        amount=AMOUNT_TO_WITHDRAW, password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    testing_cli.process_savings_withdrawal(
        amount=AMOUNT_TO_WITHDRAW2, password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ACT
    # ASSERT
    checkers.assert_pending_withrawals(
        testing_cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=AMOUNT_TO_WITHDRAW,
    )
    checkers.assert_pending_withrawals(
        testing_cli,
        account_name=f"{WORKING_ACCOUNT.name}",
        asset_amount=AMOUNT_TO_WITHDRAW2,
    )
