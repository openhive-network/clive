from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive_local_tools.cli import checkers
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log import WORKING_ACCOUNT

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT_TO_WITHDRAW: Final[tt.Asset.TestT] = tt.Asset.Test(0.111)
AMOUNT_TO_WITHDRAW2: Final[tt.Asset.TestT] = tt.Asset.Test(0.112)
AMOUNT_TO_DEPOSIT: Final[tt.Asset.TestT] = tt.Asset.Test(0.345)


async def test_show_pending_withdrawals_none(cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.show_pending_withdrawals()

    # ASSERT
    assert "no pending withdrawals" in result.stdout, "There should be no pending withdrawals."


async def test_show_pending_withdrawals_basic(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_savings_deposit(
        amount=AMOUNT_TO_DEPOSIT, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    cli_tester.process_savings_withdrawal(
        amount=AMOUNT_TO_WITHDRAW, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    cli_tester.process_savings_withdrawal(
        amount=AMOUNT_TO_WITHDRAW2, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ACT
    # ASSERT
    checkers.assert_pending_withrawals(
        cli_tester,
        account_name=WORKING_ACCOUNT.name,
        asset_amount=AMOUNT_TO_WITHDRAW,
    )
    checkers.assert_pending_withrawals(
        cli_tester,
        account_name=WORKING_ACCOUNT.name,
        asset_amount=AMOUNT_TO_WITHDRAW2,
    )
