from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.cli import checkers
from clive_local_tools.testnet_block_log import WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


async def test_show_transfer_schedule_none(cli_tester: CLITester) -> None:
    """Check proper message for account with no scheduled transfers."""
    # ARRANGE
    account_name = WORKING_ACCOUNT_DATA.account.name

    # ACT
    result = cli_tester.show_transfer_schedule(account_name=account_name)

    # ASSERT
    checkers.assert_no_exit_code_error(result)
