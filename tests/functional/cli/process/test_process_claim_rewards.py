from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.cli.commands.process.process_claim_rewards import NoRewardsToClaimError
from clive_local_tools.checkers.blockchain_checkers import (
    assert_transaction_in_blockchain,
)
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.helpers import get_formatted_error_message
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

import test_tools as tt

RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)
MEMO: Final[str] = "test-process-transfer-memo"


async def test_process_claim_rewards(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Check clive process transfer command."""
    # ACT
    result = cli_tester.process_claim_rewards()

    # ASSERT
    assert_transaction_in_blockchain(node, result)


async def test_negative_no_rewards(cli_tester: CLITester) -> None:
    # ARRANGE
    message = get_formatted_error_message(NoRewardsToClaimError())

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.process_claim_rewards()
