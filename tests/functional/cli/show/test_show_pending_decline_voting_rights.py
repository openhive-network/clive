from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.cli.checkers import (
    assert_no_pending_decline_voting_rights,
    assert_pending_decline_voting_rights,
)
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


async def test_show_pending_decline_voting_rights(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_voting_rights_decline()

    # ACT
    result = cli_tester.show_pending_decline_voting_rights()

    # ASSERT
    assert_pending_decline_voting_rights(result, WORKING_ACCOUNT_NAME)


async def test_no_pending_change(cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.show_pending_decline_voting_rights()

    # ASSERT
    assert_no_pending_decline_voting_rights(result)
