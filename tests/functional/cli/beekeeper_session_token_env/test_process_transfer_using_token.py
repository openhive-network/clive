from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import BEEKEEPER_SESSION_TOKEN_MUST_BE_SET_MESSAGE
from clive.__private.settings import settings
from clive_local_tools.checkers import assert_transaction_in_blockchain
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import (
    BEEKEEPER_SESSION_TOKEN_ENV_NAME,
    WORKING_ACCOUNT_KEY_ALIAS,
)
from clive_local_tools.testnet_block_log.constants import (
    WATCHED_ACCOUNTS_DATA,
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)
MEMO: Final[str] = "test-process-transfer-session-token-memo"


async def test_process_transfer_with_beekeeper_session_token(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Check if clive process transfer doesn't require --password when CLIVE_BEEKEEPER__SESSION_TOKEN is set."""
    # ACT
    result = cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME, amount=AMOUNT, to=RECEIVER, sign=WORKING_ACCOUNT_KEY_ALIAS, memo=MEMO
    )

    # ASSERT
    assert_transaction_in_blockchain(node, result)


async def test_process_multiple_transfers_with_beekeeper_session_token(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Check if multiple clive process doesn't require --password when CLIVE_BEEKEEPER__SESSION_TOKEN is set."""
    # ACT
    for _ in range(2):
        result = cli_tester.process_transfer(
            from_=WORKING_ACCOUNT_NAME, amount=AMOUNT, to=RECEIVER, sign=WORKING_ACCOUNT_KEY_ALIAS, memo=MEMO
        )

        # ASSERT
        assert_transaction_in_blockchain(node, result)


async def test_process_transfer_session_token_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    cli_tester: CLITester,
) -> None:
    """Check if clive process transfer throws exception when there is no pass or CLIVE_BEEKEEPER__SESSION_TOKEN set."""
    # ARRANGE
    message = (
        f"{BEEKEEPER_SESSION_TOKEN_MUST_BE_SET_MESSAGE}"
        " and a key alias to sign the transaction with if |\n| you want to broadcast it."
    )
    monkeypatch.delenv(BEEKEEPER_SESSION_TOKEN_ENV_NAME)
    settings.reload()

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.process_transfer(
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
    message = "There must be exactly one unlocked wallet with profile encryption key"

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester_with_session_token_locked.process_transfer(
            from_=WORKING_ACCOUNT_NAME, amount=tt.Asset.Hive(1), to=RECEIVER, sign=WORKING_ACCOUNT_KEY_ALIAS
        )
