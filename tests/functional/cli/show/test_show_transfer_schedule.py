from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.testnet_block_log import WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


async def test_show_pending_withdrawals_none(cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.show_transfer_schedule(account_name=WORKING_ACCOUNT_DATA.account.name)

    # ASSERT
    assert (
        f"Account `{WORKING_ACCOUNT_DATA.account.name}` has no scheduled transfers." in result.stdout
    ), "There should be no scheduled transfers."
