from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.models.schemas import EscrowDisputeOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT_NAME

from .conftest import (
    AGENT,
    RECEIVER,
    RECEIVER_KEY_ALIAS,
    approve_escrow_by_both,
    create_escrow,
)

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.cli.cli_tester import CLITester


async def test_process_escrow_dispute_by_sender(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow dispute command as sender."""
    # ARRANGE - create and fully approve an escrow first
    escrow_id = 200
    create_escrow(cli_tester, escrow_id, node)
    approve_escrow_by_both(cli_tester, escrow_id, node)

    # Switch back to sender
    cli_tester.configure_working_account_switch(account_name=WORKING_ACCOUNT_NAME)

    operation = EscrowDisputeOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        who=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
    )

    # ACT - sender raises dispute (role auto-detected)
    result = cli_tester.process_escrow_dispute(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_escrow_dispute_by_receiver(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow dispute command as receiver."""
    # ARRANGE - create and fully approve an escrow first
    escrow_id = 201
    create_escrow(cli_tester, escrow_id, node)
    approve_escrow_by_both(cli_tester, escrow_id, node)

    # Working account is already RECEIVER after approve_escrow_by_both

    operation = EscrowDisputeOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        who=RECEIVER,
        escrow_id=escrow_id,
    )

    # ACT - receiver raises dispute (role auto-detected, working account is already RECEIVER)
    result = cli_tester.process_escrow_dispute(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        sign_with=RECEIVER_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)
