from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.models.schemas import EscrowApproveOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
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


async def test_process_escrow_reject_by_agent(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow reject command as agent."""
    # ARRANGE - first create an escrow
    escrow_id = 102
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
    receiver_private_key = WATCHED_ACCOUNTS_DATA[0].account.private_key
    cli_tester.configure_key_add(key=receiver_private_key, alias=RECEIVER_KEY_ALIAS)
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
