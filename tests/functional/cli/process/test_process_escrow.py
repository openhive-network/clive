from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import EscrowInvalidDeadlineError, EscrowZeroAmountError
from clive.__private.models.schemas import (
    EscrowApproveOperation,
    EscrowDisputeOperation,
    EscrowReleaseOperation,
    EscrowTransferOperation,
    HiveDateTime,
)
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import get_formatted_error_message
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name  # bob
RECEIVER_KEY_ALIAS: Final[str] = f"{RECEIVER}_key"
AGENT: Final[str] = WATCHED_ACCOUNTS_DATA[1].account.name  # timmy
AGENT_KEY_ALIAS: Final[str] = f"{AGENT}_key"
HBD_AMOUNT: Final[tt.Asset.TbdT] = tt.Asset.Tbd(10)
HIVE_AMOUNT: Final[tt.Asset.TestT] = tt.Asset.Test(0)
FEE: Final[tt.Asset.TbdT] = tt.Asset.Tbd(1)


def _get_future_datetime(days_ahead: int) -> str:
    """Get a future datetime string in Hive format for tests.

    Uses current real time (not node time) because CLI validation compares
    against datetime.now(), not the blockchain's head block time.
    """
    from datetime import UTC, datetime, timedelta  # noqa: PLC0415

    future_time = datetime.now(UTC) + timedelta(days=days_ahead)
    return future_time.strftime("%Y-%m-%dT%H:%M:%S")


async def test_process_escrow_transfer(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow transfer command."""
    # ARRANGE
    ratification_deadline = _get_future_datetime(1)
    escrow_expiration = _get_future_datetime(7)
    escrow_id = 0

    operation = EscrowTransferOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        fee=FEE,
        ratification_deadline=HiveDateTime(ratification_deadline),
        escrow_expiration=HiveDateTime(escrow_expiration),
        json_meta="",
    )

    # ACT
    result = cli_tester.process_escrow_transfer(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        fee=FEE,
        ratification_deadline=ratification_deadline,
        escrow_expiration=escrow_expiration,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_escrow_transfer_auto_id(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow transfer with auto-calculated escrow_id."""
    # ARRANGE
    ratification_deadline = _get_future_datetime(1)
    escrow_expiration = _get_future_datetime(7)

    # ACT - don't specify escrow_id, it should be auto-calculated
    result = cli_tester.process_escrow_transfer(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        fee=FEE,
        ratification_deadline=ratification_deadline,
        escrow_expiration=escrow_expiration,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT - the command should succeed
    assert result.exit_code == 0


async def test_process_escrow_transfer_with_hive(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow transfer with HIVE amount."""
    # ARRANGE
    ratification_deadline = _get_future_datetime(1)
    escrow_expiration = _get_future_datetime(7)
    escrow_id = 10
    hive_amount = tt.Asset.Test(50)
    hbd_amount = tt.Asset.Tbd(0)
    fee = tt.Asset.Test(1)

    operation = EscrowTransferOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        hbd_amount=hbd_amount,
        hive_amount=hive_amount,
        fee=fee,
        ratification_deadline=HiveDateTime(ratification_deadline),
        escrow_expiration=HiveDateTime(escrow_expiration),
        json_meta="",
    )

    # ACT
    result = cli_tester.process_escrow_transfer(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        hbd_amount=hbd_amount,
        hive_amount=hive_amount,
        fee=fee,
        ratification_deadline=ratification_deadline,
        escrow_expiration=escrow_expiration,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_show_escrow(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test clive show escrow command."""
    # ARRANGE - create an escrow first
    ratification_deadline = _get_future_datetime(1)
    escrow_expiration = _get_future_datetime(7)
    escrow_id = 20

    cli_tester.process_escrow_transfer(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        fee=FEE,
        ratification_deadline=ratification_deadline,
        escrow_expiration=escrow_expiration,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ACT
    result = cli_tester.show_escrow(account_name=WORKING_ACCOUNT_NAME)

    # ASSERT
    assert result.exit_code == 0
    # The output should contain the escrow table or escrow information
    output = result.output.lower()
    assert "escrow" in output or RECEIVER in result.output


async def test_show_escrow_empty(
    cli_tester: CLITester,
) -> None:
    """Test clive show escrow command when no escrows exist."""
    # ARRANGE - use an account that has no escrows
    account_with_no_escrows = WATCHED_ACCOUNTS_DATA[2].account.name  # john

    # ACT
    result = cli_tester.show_escrow(account_name=account_with_no_escrows)

    # ASSERT
    assert result.exit_code == 0
    # Should show a message about no escrows
    output = result.output.lower()
    assert "no escrow" in output or "has no" in output


async def test_process_escrow_approve_by_agent(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow approve-by-agent command."""
    # ARRANGE - first create an escrow
    ratification_deadline = _get_future_datetime(1)
    escrow_expiration = _get_future_datetime(7)
    escrow_id = 100

    # Create escrow transfer
    cli_tester.process_escrow_transfer(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        fee=FEE,
        ratification_deadline=ratification_deadline,
        escrow_expiration=escrow_expiration,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # Add agent's key to the wallet
    agent_private_key = WATCHED_ACCOUNTS_DATA[1].account.private_key
    cli_tester.configure_key_add(key=agent_private_key, alias=AGENT_KEY_ALIAS)

    operation = EscrowApproveOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        who=AGENT,
        escrow_id=escrow_id,
        approve=True,
    )

    # ACT - agent approves the escrow
    result = cli_tester.process_escrow_approve_by_agent(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        sign_with=AGENT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_escrow_dispute_by_sender(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow dispute-by-sender command."""
    # ARRANGE - create and fully approve an escrow first
    ratification_deadline = _get_future_datetime(1)
    escrow_expiration = _get_future_datetime(7)
    escrow_id = 200

    # Create escrow transfer
    cli_tester.process_escrow_transfer(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        fee=FEE,
        ratification_deadline=ratification_deadline,
        escrow_expiration=escrow_expiration,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # Add keys for agent and receiver
    agent_private_key = WATCHED_ACCOUNTS_DATA[1].account.private_key
    receiver_private_key = WATCHED_ACCOUNTS_DATA[0].account.private_key
    cli_tester.configure_key_add(key=agent_private_key, alias=AGENT_KEY_ALIAS)
    cli_tester.configure_key_add(key=receiver_private_key, alias=RECEIVER_KEY_ALIAS)

    # Agent approves
    cli_tester.process_escrow_approve_by_agent(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        sign_with=AGENT_KEY_ALIAS,
    )

    # Receiver approves
    cli_tester.process_escrow_approve_by_receiver(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        sign_with=RECEIVER_KEY_ALIAS,
    )

    operation = EscrowDisputeOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        who=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
    )

    # ACT - sender raises dispute
    result = cli_tester.process_escrow_dispute_by_sender(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_escrow_release_by_sender(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow release-by-sender command."""
    # ARRANGE - create and fully approve an escrow first
    ratification_deadline = _get_future_datetime(1)
    escrow_expiration = _get_future_datetime(7)
    escrow_id = 300

    # Create escrow transfer
    cli_tester.process_escrow_transfer(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        fee=FEE,
        ratification_deadline=ratification_deadline,
        escrow_expiration=escrow_expiration,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # Add keys for agent and receiver
    agent_private_key = WATCHED_ACCOUNTS_DATA[1].account.private_key
    receiver_private_key = WATCHED_ACCOUNTS_DATA[0].account.private_key
    cli_tester.configure_key_add(key=agent_private_key, alias=AGENT_KEY_ALIAS)
    cli_tester.configure_key_add(key=receiver_private_key, alias=RECEIVER_KEY_ALIAS)

    # Agent approves
    cli_tester.process_escrow_approve_by_agent(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        sign_with=AGENT_KEY_ALIAS,
    )

    # Receiver approves
    cli_tester.process_escrow_approve_by_receiver(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        sign_with=RECEIVER_KEY_ALIAS,
    )

    operation = EscrowReleaseOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        who=WORKING_ACCOUNT_NAME,
        receiver=RECEIVER,
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
    )

    # ACT - sender releases funds to receiver
    result = cli_tester.process_escrow_release_by_sender(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        receiver=RECEIVER,
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_escrow_approve_by_receiver(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow approve-by-receiver command."""
    # ARRANGE - first create an escrow
    ratification_deadline = _get_future_datetime(1)
    escrow_expiration = _get_future_datetime(7)
    escrow_id = 101

    # Create escrow transfer
    cli_tester.process_escrow_transfer(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        fee=FEE,
        ratification_deadline=ratification_deadline,
        escrow_expiration=escrow_expiration,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # Add receiver's key to the wallet
    receiver_private_key = WATCHED_ACCOUNTS_DATA[0].account.private_key
    cli_tester.configure_key_add(key=receiver_private_key, alias=RECEIVER_KEY_ALIAS)

    operation = EscrowApproveOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        who=RECEIVER,
        escrow_id=escrow_id,
        approve=True,
    )

    # ACT - receiver approves the escrow
    result = cli_tester.process_escrow_approve_by_receiver(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        sign_with=RECEIVER_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_escrow_reject_by_agent(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow reject-by-agent command."""
    # ARRANGE - first create an escrow
    ratification_deadline = _get_future_datetime(1)
    escrow_expiration = _get_future_datetime(7)
    escrow_id = 102

    # Create escrow transfer
    cli_tester.process_escrow_transfer(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        fee=FEE,
        ratification_deadline=ratification_deadline,
        escrow_expiration=escrow_expiration,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # Add agent's key to the wallet
    agent_private_key = WATCHED_ACCOUNTS_DATA[1].account.private_key
    cli_tester.configure_key_add(key=agent_private_key, alias=AGENT_KEY_ALIAS)

    operation = EscrowApproveOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        who=AGENT,
        escrow_id=escrow_id,
        approve=False,
    )

    # ACT - agent rejects the escrow
    result = cli_tester.process_escrow_reject_by_agent(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        sign_with=AGENT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_escrow_reject_by_receiver(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow reject-by-receiver command."""
    # ARRANGE - first create an escrow
    ratification_deadline = _get_future_datetime(1)
    escrow_expiration = _get_future_datetime(7)
    escrow_id = 103

    # Create escrow transfer
    cli_tester.process_escrow_transfer(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        fee=FEE,
        ratification_deadline=ratification_deadline,
        escrow_expiration=escrow_expiration,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # Add receiver's key to the wallet
    receiver_private_key = WATCHED_ACCOUNTS_DATA[0].account.private_key
    cli_tester.configure_key_add(key=receiver_private_key, alias=RECEIVER_KEY_ALIAS)

    operation = EscrowApproveOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        who=RECEIVER,
        escrow_id=escrow_id,
        approve=False,
    )

    # ACT - receiver rejects the escrow
    result = cli_tester.process_escrow_reject_by_receiver(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        sign_with=RECEIVER_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_escrow_dispute_by_receiver(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow dispute-by-receiver command."""
    # ARRANGE - create and fully approve an escrow first
    ratification_deadline = _get_future_datetime(1)
    escrow_expiration = _get_future_datetime(7)
    escrow_id = 201

    # Create escrow transfer
    cli_tester.process_escrow_transfer(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        fee=FEE,
        ratification_deadline=ratification_deadline,
        escrow_expiration=escrow_expiration,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # Add keys for agent and receiver
    agent_private_key = WATCHED_ACCOUNTS_DATA[1].account.private_key
    receiver_private_key = WATCHED_ACCOUNTS_DATA[0].account.private_key
    cli_tester.configure_key_add(key=agent_private_key, alias=AGENT_KEY_ALIAS)
    cli_tester.configure_key_add(key=receiver_private_key, alias=RECEIVER_KEY_ALIAS)

    # Agent approves
    cli_tester.process_escrow_approve_by_agent(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        sign_with=AGENT_KEY_ALIAS,
    )

    # Receiver approves
    cli_tester.process_escrow_approve_by_receiver(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        sign_with=RECEIVER_KEY_ALIAS,
    )

    operation = EscrowDisputeOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        who=RECEIVER,
        escrow_id=escrow_id,
    )

    # ACT - receiver raises dispute
    result = cli_tester.process_escrow_dispute_by_receiver(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        sign_with=RECEIVER_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_escrow_release_by_receiver(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow release-by-receiver command."""
    # ARRANGE - create and fully approve an escrow first
    ratification_deadline = _get_future_datetime(1)
    escrow_expiration = _get_future_datetime(7)
    escrow_id = 301

    # Create escrow transfer
    cli_tester.process_escrow_transfer(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        fee=FEE,
        ratification_deadline=ratification_deadline,
        escrow_expiration=escrow_expiration,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # Add keys for agent and receiver
    agent_private_key = WATCHED_ACCOUNTS_DATA[1].account.private_key
    receiver_private_key = WATCHED_ACCOUNTS_DATA[0].account.private_key
    cli_tester.configure_key_add(key=agent_private_key, alias=AGENT_KEY_ALIAS)
    cli_tester.configure_key_add(key=receiver_private_key, alias=RECEIVER_KEY_ALIAS)

    # Agent approves
    cli_tester.process_escrow_approve_by_agent(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        sign_with=AGENT_KEY_ALIAS,
    )

    # Receiver approves
    cli_tester.process_escrow_approve_by_receiver(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        sign_with=RECEIVER_KEY_ALIAS,
    )

    operation = EscrowReleaseOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        who=RECEIVER,
        receiver=WORKING_ACCOUNT_NAME,  # receiver releases back to sender
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
    )

    # ACT - receiver releases funds back to sender
    result = cli_tester.process_escrow_release_by_receiver(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        receiver=WORKING_ACCOUNT_NAME,
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
    """Test clive process escrow release-by-agent command (after dispute)."""
    # ARRANGE - create, approve, and dispute an escrow first
    ratification_deadline = _get_future_datetime(1)
    escrow_expiration = _get_future_datetime(7)
    escrow_id = 302

    # Create escrow transfer
    cli_tester.process_escrow_transfer(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        fee=FEE,
        ratification_deadline=ratification_deadline,
        escrow_expiration=escrow_expiration,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # Add keys for agent and receiver
    agent_private_key = WATCHED_ACCOUNTS_DATA[1].account.private_key
    receiver_private_key = WATCHED_ACCOUNTS_DATA[0].account.private_key
    cli_tester.configure_key_add(key=agent_private_key, alias=AGENT_KEY_ALIAS)
    cli_tester.configure_key_add(key=receiver_private_key, alias=RECEIVER_KEY_ALIAS)

    # Agent approves
    cli_tester.process_escrow_approve_by_agent(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        sign_with=AGENT_KEY_ALIAS,
    )

    # Receiver approves
    cli_tester.process_escrow_approve_by_receiver(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        sign_with=RECEIVER_KEY_ALIAS,
    )

    # Sender raises dispute
    cli_tester.process_escrow_dispute_by_sender(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    operation = EscrowReleaseOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        who=AGENT,
        receiver=RECEIVER,  # agent decides to release to receiver
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
    )

    # ACT - agent releases funds to receiver after dispute
    result = cli_tester.process_escrow_release_by_agent(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        receiver=RECEIVER,
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        sign_with=AGENT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_escrow_transfer_zero_amount_error(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test that escrow transfer fails when both HBD and HIVE amounts are zero."""
    # ARRANGE
    ratification_deadline = _get_future_datetime(1)
    escrow_expiration = _get_future_datetime(7)
    escrow_id = 400
    zero_hbd = tt.Asset.Tbd(0)
    zero_hive = tt.Asset.Test(0)

    expected_error = get_formatted_error_message(EscrowZeroAmountError())

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_escrow_transfer(
            from_=WORKING_ACCOUNT_NAME,
            to=RECEIVER,
            agent=AGENT,
            escrow_id=escrow_id,
            hbd_amount=zero_hbd,
            hive_amount=zero_hive,
            fee=FEE,
            ratification_deadline=ratification_deadline,
            escrow_expiration=escrow_expiration,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_process_escrow_transfer_past_ratification_deadline_error(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test that escrow transfer fails when ratification deadline is in the past."""
    from datetime import UTC, datetime, timedelta  # noqa: PLC0415

    # ARRANGE - get a past datetime (relative to real time, not node time)
    past_time = datetime.now(UTC) - timedelta(days=1)
    past_ratification_deadline = past_time.strftime("%Y-%m-%dT%H:%M:%S")
    escrow_expiration = _get_future_datetime(7)
    escrow_id = 500

    expected_error = get_formatted_error_message(
        EscrowInvalidDeadlineError("Ratification deadline must be in the future.")
    )

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_escrow_transfer(
            from_=WORKING_ACCOUNT_NAME,
            to=RECEIVER,
            agent=AGENT,
            escrow_id=escrow_id,
            hbd_amount=HBD_AMOUNT,
            hive_amount=HIVE_AMOUNT,
            fee=FEE,
            ratification_deadline=past_ratification_deadline,
            escrow_expiration=escrow_expiration,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_process_escrow_transfer_expiration_before_ratification_error(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test that escrow transfer fails when escrow expiration is before ratification deadline."""
    # ARRANGE - escrow_expiration equals ratification_deadline (should fail)
    ratification_deadline = _get_future_datetime(7)
    escrow_expiration = _get_future_datetime(1)  # Earlier than ratification
    escrow_id = 600

    expected_error = get_formatted_error_message(
        EscrowInvalidDeadlineError("Escrow expiration must be after ratification deadline.")
    )

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_escrow_transfer(
            from_=WORKING_ACCOUNT_NAME,
            to=RECEIVER,
            agent=AGENT,
            escrow_id=escrow_id,
            hbd_amount=HBD_AMOUNT,
            hive_amount=HIVE_AMOUNT,
            fee=FEE,
            ratification_deadline=ratification_deadline,
            escrow_expiration=escrow_expiration,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )
