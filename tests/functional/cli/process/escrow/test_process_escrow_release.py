from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.cli.exceptions import (
    EscrowAgentReceiverRequiredError,
    EscrowAgentReleaseWithoutDisputeError,
    EscrowNotFoundError,
    EscrowReleaseNotAllowedError,
)
from clive.__private.models.schemas import EscrowReleaseOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.checkers import assert_is_working_account
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
    approve_escrow_by_both_with_who,
    create_escrow,
    create_expired_escrow,
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

    # Verify receiver is already the working account (set by approve_escrow_by_both)
    assert_is_working_account(cli_tester, RECEIVER)

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


async def test_process_escrow_receiver_release_to_self_before_expiration_error(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test that receiver cannot release to themselves before expiration."""
    # ARRANGE - create and fully approve an escrow using --who
    escrow_id = 903
    create_escrow(cli_tester, escrow_id, node)
    approve_escrow_by_both_with_who(cli_tester, escrow_id, node)

    expected_error = get_formatted_error_message(
        EscrowReleaseNotAllowedError("before expiration, receiver can only release to sender.")
    )

    # ACT & ASSERT - receiver tries to release to self using --who
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_escrow_release(
            escrow_owner=WORKING_ACCOUNT_NAME,
            escrow_id=escrow_id,
            who=RECEIVER,
            receiver=RECEIVER,
            hbd_amount=HBD_AMOUNT,
            hive_amount=HIVE_AMOUNT,
            sign_with=RECEIVER_KEY_ALIAS,
        )


async def test_process_escrow_sender_release_when_disputed_error(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test that sender cannot release funds when escrow is disputed."""
    # ARRANGE - create, approve, and dispute an escrow
    escrow_id = 904
    create_escrow(cli_tester, escrow_id, node)
    approve_escrow_by_both_with_who(cli_tester, escrow_id, node)

    # Sender raises dispute (working account is still sender)
    cli_tester.process_escrow_dispute(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )
    node.wait_number_of_blocks(1)

    expected_error = get_formatted_error_message(
        EscrowReleaseNotAllowedError("escrow is disputed, only the agent can release funds.")
    )

    # ACT & ASSERT - sender tries to release on disputed escrow
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_escrow_release(
            escrow_owner=WORKING_ACCOUNT_NAME,
            escrow_id=escrow_id,
            hbd_amount=HBD_AMOUNT,
            hive_amount=HIVE_AMOUNT,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_process_escrow_receiver_release_when_disputed_error(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test that receiver cannot release funds when escrow is disputed."""
    # ARRANGE - create, approve, and dispute an escrow
    escrow_id = 905
    create_escrow(cli_tester, escrow_id, node)
    approve_escrow_by_both_with_who(cli_tester, escrow_id, node)

    # Sender raises dispute
    cli_tester.process_escrow_dispute(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )
    node.wait_number_of_blocks(1)

    expected_error = get_formatted_error_message(
        EscrowReleaseNotAllowedError("escrow is disputed, only the agent can release funds.")
    )

    # ACT & ASSERT - receiver tries to release on disputed escrow using --who
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_escrow_release(
            escrow_owner=WORKING_ACCOUNT_NAME,
            escrow_id=escrow_id,
            who=RECEIVER,
            hbd_amount=HBD_AMOUNT,
            hive_amount=HIVE_AMOUNT,
            sign_with=RECEIVER_KEY_ALIAS,
        )


async def test_process_escrow_sender_release_to_self_after_expiration(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test that sender can release to themselves after escrow expiration."""
    # ARRANGE - create an escrow with short deadlines and wait for expiration
    escrow_id = 906
    create_expired_escrow(cli_tester, escrow_id, node)

    operation = EscrowReleaseOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        who=WORKING_ACCOUNT_NAME,
        receiver=WORKING_ACCOUNT_NAME,  # sender releases to self
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
    )

    # ACT - sender releases to self after expiration
    result = cli_tester.process_escrow_release(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        receiver=WORKING_ACCOUNT_NAME,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_escrow_receiver_release_to_self_after_expiration(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test that receiver can release to themselves after escrow expiration."""
    # ARRANGE - create an escrow with short deadlines and wait for expiration
    escrow_id = 907
    create_expired_escrow(cli_tester, escrow_id, node)

    operation = EscrowReleaseOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        who=RECEIVER,
        receiver=RECEIVER,  # receiver releases to self
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
    )

    # ACT - receiver releases to self after expiration using --who
    result = cli_tester.process_escrow_release(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        who=RECEIVER,
        receiver=RECEIVER,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        sign_with=RECEIVER_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_negative_process_escrow_agent_release_after_expiration_no_dispute(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test that agent cannot release funds from a non-disputed escrow even after expiration."""
    # ARRANGE - create an escrow with short deadlines and wait for expiration
    escrow_id = 908
    create_expired_escrow(cli_tester, escrow_id, node)

    expected_error = get_formatted_error_message(EscrowAgentReleaseWithoutDisputeError())

    # ACT & ASSERT - agent tries to release after expiration without dispute
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_escrow_release(
            escrow_owner=WORKING_ACCOUNT_NAME,
            escrow_id=escrow_id,
            who=AGENT,
            receiver=RECEIVER,
            hbd_amount=HBD_AMOUNT,
            hive_amount=HIVE_AMOUNT,
            sign_with=AGENT_KEY_ALIAS,
        )


async def test_process_escrow_release_not_found_error(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test that release fails when escrow does not exist."""
    # ARRANGE - nonexistent escrow ID
    escrow_id = 99999

    expected_error = get_formatted_error_message(EscrowNotFoundError(WORKING_ACCOUNT_NAME, escrow_id))

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_escrow_release(
            escrow_owner=WORKING_ACCOUNT_NAME,
            escrow_id=escrow_id,
            hbd_amount=HBD_AMOUNT,
            hive_amount=HIVE_AMOUNT,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )
