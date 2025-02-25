from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.cli.checkers import assert_memo_key
from clive_local_tools.testnet_block_log import WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


async def test_show_memo_key_basic(cli_tester: CLITester) -> None:
    # ACT
    # ASSERT
    assert_memo_key(cli_tester, WORKING_ACCOUNT_DATA.account.public_key)
