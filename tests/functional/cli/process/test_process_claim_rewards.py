from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.cli.commands.process.process_claim_rewards import CLIClaimRewardsZeroBalanceError
from clive.__private.models.schemas import ClaimRewardBalanceOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import get_formatted_error_message
from clive_local_tools.testnet_block_log.constants import EMPTY_ACCOUNT, WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.cli.cli_tester import CLITester


async def test_claim_rewards_success(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Test claiming rewards for alice account which has non-zero rewards from block log."""
    # ARRANGE
    account_name = WORKING_ACCOUNT_DATA.account.name
    accounts = node.api.database.find_accounts(accounts=[account_name])
    account = accounts.accounts[0]

    # ASSERT precondition - alice should have some rewards to claim
    has_rewards = (
        int(account.reward_hive_balance.amount) > 0
        or int(account.reward_hbd_balance.amount) > 0
        or int(account.reward_vesting_balance.amount) > 0
    )
    assert has_rewards, f"Account {account_name} should have rewards to claim for this test"

    operation = ClaimRewardBalanceOperation(
        account=account_name,
        reward_hive=account.reward_hive_balance,
        reward_hbd=account.reward_hbd_balance,
        reward_vests=account.reward_vesting_balance,
    )

    # ACT
    result = cli_tester.process_claim_rewards(sign_with=WORKING_ACCOUNT_KEY_ALIAS)

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_negative_claim_rewards_fails_with_zero_balance(cli_tester: CLITester) -> None:
    """Test that claiming rewards fails when account has no rewards to claim."""
    # ARRANGE
    account_name = EMPTY_ACCOUNT.name
    expected_error_message = get_formatted_error_message(CLIClaimRewardsZeroBalanceError(account_name))

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error_message):
        cli_tester.process_claim_rewards(account_name=account_name, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
