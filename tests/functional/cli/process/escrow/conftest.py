from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

BLOCK_INTERVAL: Final[int] = 3  # Hive block production interval in seconds
RATIFICATION_SECONDS: Final[int] = 30
EXPIRATION_SECONDS: Final[int] = 45

RECEIVER_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS_DATA[0].account  # bob
RECEIVER: Final[str] = RECEIVER_ACCOUNT.name
RECEIVER_KEY_ALIAS: Final[str] = f"{RECEIVER}_key"
RECEIVER_PRIVATE_KEY: Final[str] = RECEIVER_ACCOUNT.private_key
AGENT_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS_DATA[1].account  # timmy
AGENT: Final[str] = AGENT_ACCOUNT.name
AGENT_KEY_ALIAS: Final[str] = f"{AGENT}_key"
AGENT_PRIVATE_KEY: Final[str] = AGENT_ACCOUNT.private_key
HBD_AMOUNT: Final[tt.Asset.TbdT] = tt.Asset.Tbd(10)
HIVE_AMOUNT: Final[tt.Asset.TestT] = tt.Asset.Test(0)
FEE: Final[tt.Asset.TbdT] = tt.Asset.Tbd(1)


def get_future_datetime(days_ahead: int, node: tt.RawNode | None = None) -> str:
    """Get a future datetime string in Hive format for tests.

    Uses node time (head block time) because CLI validation compares
    against the blockchain's head block time, not system time.
    Falls back to system time if node is not provided.
    """
    from datetime import UTC, datetime, timedelta  # noqa: PLC0415

    if node is not None:
        gdpo = node.api.database.get_dynamic_global_properties()
        return (gdpo.time + timedelta(days=days_ahead)).strftime("%Y-%m-%dT%H:%M:%S")

    return (datetime.now(UTC) + timedelta(days=days_ahead)).strftime("%Y-%m-%dT%H:%M:%S")


def get_past_datetime(days_ago: int, node: tt.RawNode) -> str:
    """Get a past datetime string in Hive format for tests.

    Uses node time (head block time) because CLI validation compares
    against the blockchain's head block time.
    """
    from datetime import timedelta  # noqa: PLC0415

    gdpo = node.api.database.get_dynamic_global_properties()
    past_time = gdpo.time - timedelta(days=days_ago)
    return past_time.strftime("%Y-%m-%dT%H:%M:%S")


def create_escrow(
    cli_tester: CLITester,
    escrow_id: int,
    node: tt.RawNode,
    ratification_deadline: str | None = None,
    escrow_expiration: str | None = None,
) -> None:
    """Create an escrow for testing."""
    if ratification_deadline is None:
        ratification_deadline = get_future_datetime(1)
    if escrow_expiration is None:
        escrow_expiration = get_future_datetime(7)

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
    node.wait_number_of_blocks(1)


def setup_agent_and_receiver_keys(cli_tester: CLITester) -> None:
    """Add agent and receiver keys to the wallet."""
    cli_tester.configure_key_add(key=AGENT_PRIVATE_KEY, alias=AGENT_KEY_ALIAS)
    cli_tester.configure_key_add(key=RECEIVER_PRIVATE_KEY, alias=RECEIVER_KEY_ALIAS)


def get_future_datetime_seconds(seconds_ahead: int, node: tt.RawNode) -> str:
    """Get a future datetime string in Hive format, seconds ahead of node's head block time."""
    from datetime import timedelta  # noqa: PLC0415

    gdpo = node.api.database.get_dynamic_global_properties()
    return (gdpo.time + timedelta(seconds=seconds_ahead)).strftime("%Y-%m-%dT%H:%M:%S")


def approve_escrow_by_both(cli_tester: CLITester, escrow_id: int, node: tt.RawNode) -> None:
    """Approve escrow by both agent and receiver."""
    setup_agent_and_receiver_keys(cli_tester)

    # Agent approves
    cli_tester.configure_working_account_switch(account_name=AGENT)
    cli_tester.process_escrow_approve(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        sign_with=AGENT_KEY_ALIAS,
    )
    node.wait_number_of_blocks(1)

    # Receiver approves
    cli_tester.configure_working_account_switch(account_name=RECEIVER)
    cli_tester.process_escrow_approve(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        sign_with=RECEIVER_KEY_ALIAS,
    )
    node.wait_number_of_blocks(1)


def approve_escrow_by_both_with_who(cli_tester: CLITester, escrow_id: int, node: tt.RawNode) -> None:
    """Approve escrow by both agent and receiver using --who (no working account switch)."""
    setup_agent_and_receiver_keys(cli_tester)

    # Agent approves using --who
    cli_tester.process_escrow_approve(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        who=AGENT,
        sign_with=AGENT_KEY_ALIAS,
    )
    node.wait_number_of_blocks(1)

    # Receiver approves using --who
    cli_tester.process_escrow_approve(
        escrow_owner=WORKING_ACCOUNT_NAME,
        escrow_id=escrow_id,
        who=RECEIVER,
        sign_with=RECEIVER_KEY_ALIAS,
    )
    node.wait_number_of_blocks(1)


def create_expired_escrow(cli_tester: CLITester, escrow_id: int, node: tt.RawNode) -> None:
    """Create an escrow with short deadlines, approve it, and wait for it to expire.

    Uses --who for approvals to avoid working account switches.
    """
    reference_block = node.api.database.get_dynamic_global_properties().head_block_number

    ratification_deadline = get_future_datetime_seconds(RATIFICATION_SECONDS, node)
    escrow_expiration = get_future_datetime_seconds(EXPIRATION_SECONDS, node)

    create_escrow(
        cli_tester, escrow_id, node, ratification_deadline=ratification_deadline, escrow_expiration=escrow_expiration
    )
    approve_escrow_by_both_with_who(cli_tester, escrow_id, node)

    # Wait for escrow to expire: calculate remaining blocks based on elapsed time since deadlines were set
    current_block = node.api.database.get_dynamic_global_properties().head_block_number
    elapsed_blocks = current_block - reference_block
    total_blocks_to_expiration = EXPIRATION_SECONDS // BLOCK_INTERVAL + 1
    remaining = max(total_blocks_to_expiration - elapsed_blocks, 1)
    node.wait_number_of_blocks(remaining)
