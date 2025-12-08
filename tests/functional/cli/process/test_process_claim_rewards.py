from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.cli.exceptions import (
    CLIBeekeeperSessionTokenNotSetError,
    CLINoProfileUnlockedError,
    CLITransactionNotSignedError,
)
from clive.__private.models.schemas import ClaimRewardBalanceOperation
from clive.__private.cli.commands.process.process_claim_rewards import NoRewardsToClaimError
from clive_local_tools.checkers.blockchain_checkers import (
    assert_operations_placed_in_blockchain,
    assert_transaction_in_blockchain,
)
from clive_local_tools.helpers import create_transaction_filepath, get_formatted_error_message
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

import test_tools as tt

RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)
MEMO: Final[str] = "test-process-transfer-memo"


async def test_process_claim_rewards(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Check clive process transfer command."""
    # ARRANGE
    operation = ClaimRewardBalanceOperation(
        account=WORKING_ACCOUNT_NAME,
        reward_hbd=tt.Asset.Hbd(0),
        reward_hive=tt.Asset.Hive(0),
        reward_vests=tt.Asset.Vest(0),
    )

    # ACT
    result = cli_tester.process_claim_rewards()

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_negative_no_rewards(cli_tester: CLITester) -> None:
    # ARRANGE
    message = get_formatted_error_message(NoRewardsToClaimError())

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.process_claim_rewards()