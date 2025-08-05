from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive.__private.core.constants.node_special_assets import DELEGATION_REMOVE_ASSETS
from clive.__private.models.schemas import DelegateVestingSharesOperation
from clive_local_tools.checkers.blockchain_checkers import (
    assert_operations_placed_in_blockchain,
    assert_transaction_in_blockchain,
)
from clive_local_tools.cli.checkers import assert_no_delegations
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT_TO_DELEGATE: Final[tt.Asset.VestT] = tt.Asset.Vest(2345.678)
DELEGATEE_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS_DATA[0].account


async def test_delegations_set_use_vests(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    operation = DelegateVestingSharesOperation(
        delegator=WORKING_ACCOUNT_DATA.account.name,
        delegatee=DELEGATEE_ACCOUNT.name,
        vesting_shares=AMOUNT_TO_DELEGATE,
    )

    # ACT
    result = cli_tester.process_delegations_set(
        delegatee=operation.delegatee, amount=AMOUNT_TO_DELEGATE, sign_with=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_delegations_set_use_hive(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    amount_to_delegate_hp: Final[tt.Asset.VestT] = tt.Asset.Vest(4567.890)

    # ACT
    result = cli_tester.process_delegations_set(
        delegatee=DELEGATEE_ACCOUNT.name, amount=amount_to_delegate_hp, sign_with=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT
    assert_transaction_in_blockchain(node, result)


async def test_delegations_reset(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    amount_to_delegate_reset: Final[tt.Asset.VestT] = tt.Asset.Vest(3456.789)
    cli_tester.process_delegations_set(
        delegatee=DELEGATEE_ACCOUNT.name, amount=AMOUNT_TO_DELEGATE, sign_with=WORKING_ACCOUNT_KEY_ALIAS
    )
    operation = DelegateVestingSharesOperation(
        delegator=WORKING_ACCOUNT_DATA.account.name,
        delegatee=DELEGATEE_ACCOUNT.name,
        vesting_shares=amount_to_delegate_reset,
    )

    # ACT
    result = cli_tester.process_delegations_set(
        delegatee=operation.delegatee, amount=amount_to_delegate_reset, sign_with=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_delegations_remove(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_delegations_set(
        delegatee=DELEGATEE_ACCOUNT.name, amount=AMOUNT_TO_DELEGATE, sign_with=WORKING_ACCOUNT_KEY_ALIAS
    )
    operation = DelegateVestingSharesOperation(
        delegator=WORKING_ACCOUNT_DATA.account.name,
        delegatee=DELEGATEE_ACCOUNT.name,
        vesting_shares=DELEGATION_REMOVE_ASSETS[1],
    )

    # ACT
    result = cli_tester.process_delegations_remove(delegatee=operation.delegatee, sign_with=WORKING_ACCOUNT_KEY_ALIAS)

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)
    assert_no_delegations(cli_tester)
