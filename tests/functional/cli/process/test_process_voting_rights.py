from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.models.schemas import DeclineVotingRightsOperation

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.cli.cli_tester import CLITester

from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT_NAME


async def test_decline(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    operation = DeclineVotingRightsOperation(account=WORKING_ACCOUNT_NAME, decline=True)

    # ACT
    result = cli_tester.process_voting_rights_decline()

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_cancel_decline(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_voting_rights_decline()
    operation = DeclineVotingRightsOperation(account=WORKING_ACCOUNT_NAME, decline=False)

    # ACT
    result = cli_tester.process_voting_rights_cancel_decline()

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)
