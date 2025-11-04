from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.cli.checkers import (
    assert_no_pending_change_recovery_account,
    assert_pending_change_recovery_account,
)
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_NAMES, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


async def test_show_pending_change_recovery_account(cli_tester: CLITester) -> None:
    # ARRANGE
    new_recovery_account = WATCHED_ACCOUNTS_NAMES[0]
    cli_tester.process_change_recovery_account(new_recovery_account=new_recovery_account)

    # ACT
    result = cli_tester.show_pending_change_recovery_account()

    # ASSERT
    assert_pending_change_recovery_account(result, WORKING_ACCOUNT_NAME, new_recovery_account)


async def test_no_pending_change(cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.show_pending_change_recovery_account()

    # ASSERT
    assert_no_pending_change_recovery_account(result)
