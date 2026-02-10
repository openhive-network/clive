from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.cli.exceptions import EscrowOperationNotAllowedForRoleError
from clive.__private.models.schemas import EscrowApproveOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import get_formatted_error_message
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT_NAME

from .conftest import (
    AGENT,
    AGENT_KEY_ALIAS,
    AGENT_PRIVATE_KEY,
    BLOCK_INTERVAL,
    EXPIRATION_SECONDS,
    RATIFICATION_SECONDS,
    RECEIVER,
    RECEIVER_KEY_ALIAS,
    RECEIVER_PRIVATE_KEY,
    create_escrow,
    get_future_datetime_seconds,
)

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.cli.cli_tester import CLITester


async def test_process_escrow_reject_by_agent(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow reject command as agent."""
    # ARRANGE - first create an escrow
    escrow_id = 102
    create_escrow(cli_tester, escrow_id, node)

    # Add agent's key to the wallet and switch working account
    cli_tester.configure_key_add(key=AGENT_PRIVATE_KEY, alias=AGENT_KEY_ALIAS)
    cli_tester.configure_working_account_switch(account_name=AGENT)

    operation = EscrowApproveOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        who=AGENT,
        escrow_id=escrow_id,
        approve=False,
    )

    # ACT - agent rejects the escrow (role auto-detected)
    result = cli_tester.process_escrow_reject(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        sign_with=AGENT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_escrow_reject_by_receiver(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow reject command as receiver."""
    # ARRANGE - first create an escrow
    escrow_id = 103
    create_escrow(cli_tester, escrow_id, node)

    # Add receiver's key to the wallet and switch working account
    cli_tester.configure_key_add(key=RECEIVER_PRIVATE_KEY, alias=RECEIVER_KEY_ALIAS)
    cli_tester.configure_working_account_switch(account_name=RECEIVER)

    operation = EscrowApproveOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        who=RECEIVER,
        escrow_id=escrow_id,
        approve=False,
    )

    # ACT - receiver rejects the escrow (role auto-detected)
    result = cli_tester.process_escrow_reject(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        sign_with=RECEIVER_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_escrow_reject_sender_not_allowed_error(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test that sender cannot reject their own escrow."""
    # ARRANGE - create an escrow (working account is the sender)
    escrow_id = 110
    create_escrow(cli_tester, escrow_id, node)

    expected_error = get_formatted_error_message(
        EscrowOperationNotAllowedForRoleError("sender", "approve/reject", ("receiver", "agent"))
    )

    # ACT & ASSERT - sender (working account=alice, no --who) tries to reject
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_escrow_reject(
            escrow_owner=WORKING_ACCOUNT_NAME,
            escrow_id=escrow_id,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_process_escrow_reject_after_ratification_deadline_error(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test that rejecting an escrow after the ratification deadline fails."""
    # ARRANGE - create an escrow with short ratification deadline
    escrow_id = 111
    reference_block = node.api.database.get_dynamic_global_properties().head_block_number

    ratification_deadline = get_future_datetime_seconds(RATIFICATION_SECONDS, node)
    escrow_expiration = get_future_datetime_seconds(EXPIRATION_SECONDS, node)

    create_escrow(
        cli_tester,
        escrow_id,
        node,
        ratification_deadline=ratification_deadline,
        escrow_expiration=escrow_expiration,
    )

    # Wait for ratification deadline to pass
    current_block = node.api.database.get_dynamic_global_properties().head_block_number
    elapsed_blocks = current_block - reference_block
    total_blocks_to_ratification = RATIFICATION_SECONDS // BLOCK_INTERVAL + 1
    remaining = max(total_blocks_to_ratification - elapsed_blocks, 1)
    node.wait_number_of_blocks(remaining)

    # Add agent's key and switch to agent
    cli_tester.configure_key_add(key=AGENT_PRIVATE_KEY, alias=AGENT_KEY_ALIAS)
    cli_tester.configure_working_account_switch(account_name=AGENT)

    # ACT & ASSERT - agent tries to reject after ratification deadline has passed
    # The blockchain auto-removes unapproved escrows once the ratification deadline passes,
    # so the escrow will no longer be found on-chain.
    with pytest.raises(
        CLITestCommandError, match=f"Escrow with ID {escrow_id} not found for account `{WORKING_ACCOUNT_NAME}`"
    ):
        cli_tester.process_escrow_reject(
            escrow_owner=WORKING_ACCOUNT_NAME,
            escrow_id=escrow_id,
            sign_with=AGENT_KEY_ALIAS,
        )
