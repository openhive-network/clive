from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.cli.exceptions import EscrowAgentReceiverRequiredError, EscrowReleaseNotAllowedError
from clive.__private.models.schemas import EscrowReleaseOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import get_formatted_error_message
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT_NAME

from .conftest import (
    AGENT,
    AGENT_KEY_ALIAS,
    HBD_AMOUNT,
    HIVE_AMOUNT,
    RECEIVER,
    RECEIVER_KEY_ALIAS,
    approve_escrow_by_both,
    create_escrow,
)

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.cli.cli_tester import CLITester


async def test_process_escrow_release_by_sender(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow release command as sender."""
    # ARRANGE - create and fully approve an escrow first
    escrow_id = 300
    create_escrow(cli_tester, escrow_id, node)
    approve_escrow_by_both(cli_tester, escrow_id, node)

    # Switch back to sender
    cli_tester.configure_working_account_switch(account_name=WORKING_ACCOUNT_NAME)

    operation = EscrowReleaseOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        who=WORKING_ACCOUNT_NAME,
        receiver=RECEIVER,  # auto-filled: sender releases to receiver
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
    )

    # ACT - sender releases funds to receiver (receiver auto-filled)
    result = cli_tester.process_escrow_release(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_escrow_release_by_receiver(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow release command as receiver."""
    # ARRANGE - create and fully approve an escrow first
    escrow_id = 301
    create_escrow(cli_tester, escrow_id, node)
    approve_escrow_by_both(cli_tester, escrow_id, node)

    # Working account is already RECEIVER after approve_escrow_by_both

    operation = EscrowReleaseOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        who=RECEIVER,
        receiver=WORKING_ACCOUNT_NAME,  # auto-filled: receiver releases to sender
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
    )

    # ACT - receiver releases funds back to sender (receiver auto-filled)
    result = cli_tester.process_escrow_release(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        sign_with=RECEIVER_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_escrow_release_by_agent(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow release command as agent (after dispute)."""
    # ARRANGE - create, approve, and dispute an escrow first
    escrow_id = 302
    create_escrow(cli_tester, escrow_id, node)
    approve_escrow_by_both(cli_tester, escrow_id, node)

    # Sender raises dispute
    cli_tester.configure_working_account_switch(account_name=WORKING_ACCOUNT_NAME)
    cli_tester.process_escrow_dispute(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )
    node.wait_number_of_blocks(1)

    # Switch to agent
    cli_tester.configure_working_account_switch(account_name=AGENT)

    operation = EscrowReleaseOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        who=AGENT,
        receiver=RECEIVER,  # agent must specify receiver explicitly
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
    )

    # ACT - agent releases funds to receiver after dispute (must specify --receiver)
    result = cli_tester.process_escrow_release(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        receiver=RECEIVER,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        sign_with=AGENT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_escrow_agent_receiver_required_error(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test that agent must specify --receiver when releasing funds."""
    # ARRANGE - create, approve, and dispute an escrow first
    escrow_id = 900
    create_escrow(cli_tester, escrow_id, node)
    approve_escrow_by_both(cli_tester, escrow_id, node)

    # Sender raises dispute
    cli_tester.configure_working_account_switch(account_name=WORKING_ACCOUNT_NAME)
    cli_tester.process_escrow_dispute(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )
    node.wait_number_of_blocks(1)

    # Switch to agent
    cli_tester.configure_working_account_switch(account_name=AGENT)

    expected_error = get_formatted_error_message(EscrowAgentReceiverRequiredError())

    # ACT & ASSERT - agent tries to release without --receiver
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_escrow_release(
            escrow_owner=WORKING_ACCOUNT_NAME,
            escrow_id=escrow_id,
            # no receiver specified - should fail
            hbd_amount=HBD_AMOUNT,
            hive_amount=HIVE_AMOUNT,
            sign_with=AGENT_KEY_ALIAS,
        )


async def test_process_escrow_sender_release_to_self_before_expiration_error(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test that sender cannot release to themselves before expiration."""
    # ARRANGE - create and fully approve an escrow first
    escrow_id = 901
    create_escrow(cli_tester, escrow_id, node)
    approve_escrow_by_both(cli_tester, escrow_id, node)

    # Switch back to sender
    cli_tester.configure_working_account_switch(account_name=WORKING_ACCOUNT_NAME)

    expected_error = get_formatted_error_message(
        EscrowReleaseNotAllowedError("before expiration, sender can only release to receiver.")
    )

    # ACT & ASSERT - sender tries to release to themselves (should fail before expiration)
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_escrow_release(
            escrow_owner=WORKING_ACCOUNT_NAME,
            escrow_id=escrow_id,
            receiver=WORKING_ACCOUNT_NAME,  # sender tries to release to self
            hbd_amount=HBD_AMOUNT,
            hive_amount=HIVE_AMOUNT,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_process_escrow_agent_release_before_dispute_error(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test that agent cannot release funds before a dispute is raised."""
    # ARRANGE - create and fully approve an escrow (but no dispute)
    escrow_id = 902
    create_escrow(cli_tester, escrow_id, node)
    approve_escrow_by_both(cli_tester, escrow_id, node)

    # Switch to agent (keys already added by approve_escrow_by_both)
    cli_tester.configure_working_account_switch(account_name=AGENT)

    expected_error = get_formatted_error_message(
        EscrowReleaseNotAllowedError("agent can only release after a dispute has been raised.")
    )

    # ACT & ASSERT - agent tries to release before dispute (should fail)
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_escrow_release(
            escrow_owner=WORKING_ACCOUNT_NAME,
            escrow_id=escrow_id,
            receiver=RECEIVER,
            hbd_amount=HBD_AMOUNT,
            hive_amount=HIVE_AMOUNT,
            sign_with=AGENT_KEY_ALIAS,
        )
