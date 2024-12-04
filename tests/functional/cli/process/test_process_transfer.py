from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.cli.exceptions import BEEKEEPER_SESSION_TOKEN_MUST_BE_SET_MESSAGE
from clive.__private.core.beekeeper.handle import Beekeeper
from clive_local_tools.checkers.blockchain_checkers import (
    assert_operations_placed_in_blockchain,
    assert_transaction_in_blockchain,
)
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import BEEKEEPER_SESSION_TOKEN_ENV_NAME, WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_NAME
from schemas.operations import TransferOperation

if TYPE_CHECKING:
    from typing import AsyncGenerator

    from clive_local_tools.cli.cli_tester import CLITester

import test_tools as tt

RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)
MEMO: Final[str] = "test-process-transfer-memo"


@pytest.fixture
async def beekeeper_for_remote_use() -> AsyncGenerator[Beekeeper]:
    async with Beekeeper() as beekeeper:
        yield beekeeper


async def test_process_transfer(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Check clive process transfer command."""
    # ARRANGE
    operation = TransferOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
    )

    # ACT
    result = cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=tt.Asset.Hive(1),
        to=RECEIVER,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        memo=MEMO,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_transfer_with_remote_beekeeper_option(
    node: tt.RawNode, beekeeper_for_remote_use: Beekeeper, cli_tester: CLITester
) -> None:
    """Check clive process transfer command."""
    # ARRANGE
    beekeeper_http_endpoint = beekeeper_for_remote_use.http_endpoint.as_string()
    operation = TransferOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
    )
    log_message = f"Using beekeeper at {beekeeper_http_endpoint}"

    # ACT
    result = cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=tt.Asset.Hive(1),
        to=RECEIVER,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        memo=MEMO,
        beekeeper_remote=beekeeper_http_endpoint,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)
    assert log_message in result.output, f"Command process transfer should use beekeeper at `{beekeeper_http_endpoint}`"


async def test_process_multiple_transfers_with_beekeeper_session_token(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Check if multiple clive process transfer when CLIVE_BEEKEEPER__SESSION_TOKEN is set."""
    # ACT
    for _ in range(2):
        result = cli_tester.process_transfer(
            from_=WORKING_ACCOUNT_NAME, amount=AMOUNT, to=RECEIVER, sign=WORKING_ACCOUNT_KEY_ALIAS, memo=MEMO
        )

        # ASSERT
        assert_transaction_in_blockchain(node, result)


async def test_process_transfer_with_beekeeper_session_token_missing(
    cli_tester_without_session_token: CLITester,
) -> None:
    """Check if clive process transfer throws exception when there is no CLIVE_BEEKEEPER__SESSION_TOKEN set."""
    # ARRANGE
    message = (
        f"{BEEKEEPER_SESSION_TOKEN_MUST_BE_SET_MESSAGE}"
        " and a key alias to sign the transaction with if |\n| you want to broadcast it."
    )

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester_without_session_token.process_transfer(
            from_=WORKING_ACCOUNT_NAME,
            amount=tt.Asset.Hive(1),
            to=RECEIVER,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_process_transfer_with_beekeeper_session_token_not_unlocked(
    cli_tester_with_session_token_locked: CLITester,
) -> None:
    """Check if clive process transfer throws exception when wallet is not unlocked."""
    # ARRANGE
    message = (
        f"If you want to use {BEEKEEPER_SESSION_TOKEN_ENV_NAME} envvar,"
        f" ensure it is in unlocked state for wallet {WORKING_ACCOUNT_NAME}."
    )

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester_with_session_token_locked.process_transfer(
            from_=WORKING_ACCOUNT_NAME, amount=tt.Asset.Hive(1), to=RECEIVER, sign=WORKING_ACCOUNT_KEY_ALIAS
        )


async def test_process_transfer_with_beekeeper_session_token_unlocked_without_sign(
    cli_tester: CLITester,
) -> None:
    """Check if clive process transfer without sign throws exception when wallet is unlocked."""
    # ARRANGE
    message = "Could not broadcast unsigned transaction."

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.process_transfer(from_=WORKING_ACCOUNT_NAME, amount=tt.Asset.Hive(1), to=RECEIVER)
