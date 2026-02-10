from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.cli.exceptions import EscrowNotApprovedError, EscrowOperationNotAllowedForRoleError
from clive.__private.models.schemas import EscrowDisputeOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import get_formatted_error_message
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT_NAME

from .conftest import (
    AGENT,
    AGENT_KEY_ALIAS,
    RECEIVER,
    RECEIVER_KEY_ALIAS,
    approve_escrow_by_both,
    approve_escrow_by_both_with_who,
    create_escrow,
    create_expired_escrow,
    setup_agent_and_receiver_keys,
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


async def test_process_escrow_dispute_agent_not_allowed_error(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test that agent cannot dispute an escrow."""
    # ARRANGE - create and fully approve an escrow
    escrow_id = 202
    create_escrow(cli_tester, escrow_id, node)
    approve_escrow_by_both_with_who(cli_tester, escrow_id, node)

    expected_error = get_formatted_error_message(
        EscrowOperationNotAllowedForRoleError("agent", "dispute", ("sender", "receiver"))
    )

    # ACT & ASSERT - agent tries to dispute using --who
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_escrow_dispute(
            escrow_owner=WORKING_ACCOUNT_NAME,
            escrow_id=escrow_id,
            who=AGENT,
            sign_with=AGENT_KEY_ALIAS,
        )


async def test_process_escrow_dispute_not_approved_error(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test that dispute fails when escrow is not fully approved."""
    # ARRANGE - create an escrow and only have agent approve
    escrow_id = 203
    create_escrow(cli_tester, escrow_id, node)

    setup_agent_and_receiver_keys(cli_tester)

    # Only agent approves (using --who)
    cli_tester.process_escrow_approve(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        who=AGENT,
        sign_with=AGENT_KEY_ALIAS,
    )
    node.wait_number_of_blocks(1)

    expected_error = get_formatted_error_message(EscrowNotApprovedError())

    # ACT & ASSERT - sender tries to dispute (not fully approved)
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_escrow_dispute(
            escrow_owner=WORKING_ACCOUNT_NAME,
            escrow_id=escrow_id,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_process_escrow_dispute_double_error(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test that disputing an already disputed escrow fails."""
    # ARRANGE - create and fully approve an escrow, then dispute it
    escrow_id = 204
    create_escrow(cli_tester, escrow_id, node)
    approve_escrow_by_both(cli_tester, escrow_id, node)

    # First dispute by receiver (working account is already RECEIVER after approve_escrow_by_both)
    cli_tester.process_escrow_dispute(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        sign_with=RECEIVER_KEY_ALIAS,
    )
    node.wait_number_of_blocks(1)

    # Switch to sender for second dispute
    cli_tester.configure_working_account_switch(account_name=WORKING_ACCOUNT_NAME)

    # ACT & ASSERT - second dispute is rejected by the blockchain
    with pytest.raises(CLITestCommandError, match="The escrow is already under dispute"):
        cli_tester.process_escrow_dispute(
            escrow_owner=WORKING_ACCOUNT_NAME,
            escrow_id=escrow_id,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_process_escrow_dispute_after_expiration_error(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test that disputing an expired escrow fails."""
    # ARRANGE - create an escrow with short deadlines, approve it, and wait for expiration
    escrow_id = 205
    create_expired_escrow(cli_tester, escrow_id, node)

    # ACT & ASSERT - dispute after expiration is rejected by the blockchain
    with pytest.raises(CLITestCommandError, match="Disputing the escrow must happen before expiration"):
        cli_tester.process_escrow_dispute(
            escrow_owner=WORKING_ACCOUNT_NAME,
            escrow_id=escrow_id,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )
