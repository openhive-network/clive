from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.cli.exceptions import EscrowRoleDetectionError
from clive.__private.models.schemas import EscrowApproveOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.helpers import get_formatted_error_message
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_NAME

from .conftest import (
    AGENT,
    AGENT_KEY_ALIAS,
    RECEIVER,
    RECEIVER_KEY_ALIAS,
    create_escrow,
)

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.cli.cli_tester import CLITester


async def test_process_escrow_approve_by_agent(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow approve command as agent."""
    # ARRANGE - first create an escrow
    escrow_id = 100
    create_escrow(cli_tester, escrow_id, node)

    # Add agent's key to the wallet and switch working account
    agent_private_key = WATCHED_ACCOUNTS_DATA[1].account.private_key
    cli_tester.configure_key_add(key=agent_private_key, alias=AGENT_KEY_ALIAS)
    cli_tester.configure_working_account_switch(account_name=AGENT)

    operation = EscrowApproveOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        who=AGENT,
        escrow_id=escrow_id,
        approve=True,
    )

    # ACT - agent approves the escrow (role auto-detected)
    result = cli_tester.process_escrow_approve(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        sign_with=AGENT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_escrow_approve_by_receiver(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow approve command as receiver."""
    # ARRANGE - first create an escrow
    escrow_id = 101
    create_escrow(cli_tester, escrow_id, node)

    # Add receiver's key to the wallet and switch working account
    receiver_private_key = WATCHED_ACCOUNTS_DATA[0].account.private_key
    cli_tester.configure_key_add(key=receiver_private_key, alias=RECEIVER_KEY_ALIAS)
    cli_tester.configure_working_account_switch(account_name=RECEIVER)

    operation = EscrowApproveOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        who=RECEIVER,
        escrow_id=escrow_id,
        approve=True,
    )

    # ACT - receiver approves the escrow (role auto-detected)
    result = cli_tester.process_escrow_approve(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        sign_with=RECEIVER_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_escrow_approve_with_who_override(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow approve with --who option for delegated authority."""
    # ARRANGE - first create an escrow
    escrow_id = 104
    create_escrow(cli_tester, escrow_id, node)

    # Add agent's key to the wallet (we have delegated authority to sign for agent)
    agent_private_key = WATCHED_ACCOUNTS_DATA[1].account.private_key
    cli_tester.configure_key_add(key=agent_private_key, alias=AGENT_KEY_ALIAS)

    # Working account stays as WORKING_ACCOUNT_NAME (sender), but we use --who to act as agent
    operation = EscrowApproveOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        who=AGENT,  # Acting as agent via --who
        escrow_id=escrow_id,
        approve=True,
    )

    # ACT - use --who to specify we're acting as agent (delegated authority)
    result = cli_tester.process_escrow_approve(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        who=AGENT,  # Override role detection
        sign_with=AGENT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_escrow_role_detection_error(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test that escrow command fails when working account is not a party to escrow."""
    # ARRANGE - first create an escrow
    escrow_id = 700
    create_escrow(cli_tester, escrow_id, node)

    # Switch to an account that is not part of the escrow (john is already tracked via WATCHED_ACCOUNTS_DATA)
    unrelated_account = WATCHED_ACCOUNTS_DATA[2].account.name  # john
    cli_tester.configure_working_account_switch(account_name=unrelated_account)
    unrelated_private_key = WATCHED_ACCOUNTS_DATA[2].account.private_key
    unrelated_key_alias = f"{unrelated_account}_key"
    cli_tester.configure_key_add(key=unrelated_private_key, alias=unrelated_key_alias)

    expected_error = get_formatted_error_message(
        EscrowRoleDetectionError(unrelated_account, WORKING_ACCOUNT_NAME, RECEIVER, AGENT)
    )

    # ACT & ASSERT - working account is not a party to escrow (for approve, valid roles are receiver/agent)
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_escrow_approve(
            escrow_owner=WORKING_ACCOUNT_NAME,
            escrow_id=escrow_id,
            sign_with=unrelated_key_alias,
        )
