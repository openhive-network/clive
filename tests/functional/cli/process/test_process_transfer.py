from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.cli.exceptions import (
    CLIBeekeeperSessionTokenNotSetError,
    CLINoProfileUnlockedError,
    CLITransactionNotSignedError,
)
from clive.__private.models.schemas import TransferOperation
from clive_local_tools.checkers.blockchain_checkers import (
    assert_operations_placed_in_blockchain,
    assert_transaction_in_blockchain,
)
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

import test_tools as tt

RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)
MEMO: Final[str] = "test-process-transfer-memo"


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
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=MEMO,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_multiple_transfers_when_unlocked_once(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Check if multiple transfers can be done when unlocked once."""
    # ACT
    for _ in range(2):
        result = cli_tester.process_transfer(
            from_=WORKING_ACCOUNT_NAME, amount=AMOUNT, to=RECEIVER, sign_with=WORKING_ACCOUNT_KEY_ALIAS, memo=MEMO
        )

        # ASSERT
        assert_transaction_in_blockchain(node, result)


async def test_process_transfer_with_beekeeper_session_token_missing(
    cli_tester_without_session_token: CLITester,
) -> None:
    """Check if clive process transfer throws exception when there is no CLIVE_BEEKEEPER__SESSION_TOKEN set."""
    # ARRANGE
    message = CLIBeekeeperSessionTokenNotSetError.MESSAGE

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester_without_session_token.process_transfer(
            from_=WORKING_ACCOUNT_NAME,
            amount=tt.Asset.Hive(1),
            to=RECEIVER,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_process_transfer_in_locked(
    cli_tester_locked: CLITester,
) -> None:
    """Check if clive process transfer throws exception when wallet is locked."""
    # ARRANGE
    message = CLINoProfileUnlockedError.MESSAGE

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester_locked.process_transfer(
            from_=WORKING_ACCOUNT_NAME, amount=tt.Asset.Hive(1), to=RECEIVER, sign_with=WORKING_ACCOUNT_KEY_ALIAS
        )


async def test_process_transfer_in_unlocked_without_sign(
    cli_tester: CLITester,
) -> None:
    """Check if clive process transfer without sign_with throws exception when wallet is unlocked."""
    # ARRANGE
    message = CLITransactionNotSignedError.MESSAGE

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.process_transfer(from_=WORKING_ACCOUNT_NAME, amount=tt.Asset.Hive(1), to=RECEIVER, autosign=False)
