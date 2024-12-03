from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive_local_tools.checkers.blockchain_checkers import assert_transaction_in_blockchain
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
    from pathlib import Path

    from clive_local_tools.cli.cli_tester import CLITester


RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT_TO_POWER_UP: Final[tt.Asset.HiveT] = tt.Asset.Hive(765.432)


def trx_file(temporary_path_per_test: Path) -> Path:
    return temporary_path_per_test / "power_up.json"


async def test_process_signed_transaction(
    node: tt.RawNode,
    cli_tester_with_session_token_unlocked: CLITester,
    tmp_path: Path,
) -> None:
    """Check if clive process transfer doesn't require --password when CLIVE_BEEKEEPER__SESSION_TOKEN is set."""
    # ARRANGE
    cli_tester_with_session_token_unlocked.process_power_up(
        amount=AMOUNT_TO_POWER_UP,
        to=RECEIVER,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        broadcast=False,
        save_file=trx_file(tmp_path),
    )

    # ACT
    result = cli_tester_with_session_token_unlocked.process_transaction(
        already_signed_mode="multisign",
        from_file=trx_file(tmp_path),
    )

    # ASSERT
    assert_transaction_in_blockchain(node, result)


async def test_process_unsigned_transaction(
    node: tt.RawNode,
    cli_tester_with_session_token_unlocked: CLITester,
    tmp_path: Path,
) -> None:
    """Check if clive process transfer doesn't require --password when CLIVE_BEEKEEPER__SESSION_TOKEN is set."""
    # ARRANGE
    cli_tester_with_session_token_unlocked.process_power_up(
        amount=AMOUNT_TO_POWER_UP,
        to=RECEIVER,
        broadcast=False,
        save_file=trx_file(tmp_path),
    )

    # ACT
    result = cli_tester_with_session_token_unlocked.process_transaction(
        already_signed_mode="multisign",
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        from_file=trx_file(tmp_path),
    )

    # ASSERT
    assert_transaction_in_blockchain(node, result)


async def test_session_token_not_unlocked(
    cli_tester_with_session_token_locked: CLITester,
    tmp_path: Path,
) -> None:
    """Check if clive process transfer throws exception when wallet is not unlocked."""
    # ARRANGE
    message = (
        f"If you want to use {BEEKEEPER_SESSION_TOKEN_ENV_NAME} envvar,"
        f" ensure it is in unlocked state for wallet {WORKING_ACCOUNT_NAME}."
    )
    cli_tester_with_session_token_locked.process_power_up(
        amount=AMOUNT_TO_POWER_UP,
        to=RECEIVER,
        broadcast=False,
        save_file=trx_file(tmp_path),
    )

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester_with_session_token_locked.process_transaction(
            already_signed_mode="multisign",
            sign=WORKING_ACCOUNT_KEY_ALIAS,
            from_file=trx_file(tmp_path),
        )
