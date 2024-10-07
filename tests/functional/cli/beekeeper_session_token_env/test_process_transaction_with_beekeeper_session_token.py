from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.core.commands.lock import Lock
from clive_local_tools.checkers import assert_transaction_in_blockchain
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import (
    WORKING_ACCOUNT_KEY_ALIAS,
)
from clive_local_tools.testnet_block_log.constants import (
    WATCHED_ACCOUNTS_DATA,
)

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.core.profile import Profile
    from clive_local_tools.cli.cli_tester import CLITester


RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT_TO_POWER_UP: Final[tt.Asset.HiveT] = tt.Asset.Hive(765.432)


def trx_file(temporary_path_per_test: Path) -> Path:
    return temporary_path_per_test / "power_up.json"


async def test_process_signed_transaction(
    node: tt.RawNode,
    cli_tester: CLITester,
    tmp_path: Path,
) -> None:
    """Check if clive process transfer doesn't require --password when CLIVE_BEEKEEPER__SESSION_TOKEN is set."""
    # ARRANGE
    cli_tester.process_power_up(
        amount=AMOUNT_TO_POWER_UP,
        to=RECEIVER,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        broadcast=False,
        save_file=trx_file(tmp_path),
    )

    # ACT
    result = cli_tester.process_transaction(
        already_signed_mode="multisign",
        from_file=trx_file(tmp_path),
    )

    # ASSERT
    assert_transaction_in_blockchain(node, result)


async def test_process_unsigned_transaction(
    node: tt.RawNode,
    cli_tester: CLITester,
    tmp_path: Path,
) -> None:
    """Check if clive process transfer doesn't require --password when CLIVE_BEEKEEPER__SESSION_TOKEN is set."""
    # ARRANGE
    cli_tester.process_power_up(
        amount=AMOUNT_TO_POWER_UP,
        to=RECEIVER,
        broadcast=False,
        save_file=trx_file(tmp_path),
    )

    # ACT
    result = cli_tester.process_transaction(
        already_signed_mode="multisign",
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        from_file=trx_file(tmp_path),
    )

    # ASSERT
    assert_transaction_in_blockchain(node, result)


async def test_session_token_not_unlocked(
    beekeeper: Beekeeper,
    prepare_profile_with_session: Profile,
    cli_tester: CLITester,
    tmp_path: Path,
) -> None:
    """Check if clive process transfer throws exception when wallet is not unlocked."""
    # ARRANGE
    message = "Beekeeper session must be unlocked for one profile."
    cli_tester.process_power_up(
        amount=AMOUNT_TO_POWER_UP,
        to=RECEIVER,
        broadcast=False,
        save_file=trx_file(tmp_path),
    )
    await Lock(beekeeper=beekeeper, wallet=prepare_profile_with_session.name).execute()

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.process_transaction(
            already_signed_mode="multisign",
            sign=WORKING_ACCOUNT_KEY_ALIAS,
            from_file=trx_file(tmp_path),
        )
