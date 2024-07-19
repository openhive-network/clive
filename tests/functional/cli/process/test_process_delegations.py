from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive.__private.core.constants.node import VESTS_TO_REMOVE_DELEGATION
from clive.models.asset import Asset
from clive_local_tools.checkers import assert_operations_placed_in_blockchain, assert_transaction_in_blockchain
from clive_local_tools.cli.checkers import assert_no_delegations
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA
from schemas.operations import DelegateVestingSharesOperation

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT_TO_DELEGATE1: Final[tt.Asset.VestT] = tt.Asset.Vest(2345.678)
AMOUNT_TO_DELEGATE2: Final[tt.Asset.VestT] = tt.Asset.Vest(3456.789)
AMOUNT_TO_DELEGATE3: Final[tt.Asset.HiveT] = tt.Asset.Hive(4567.890)
DELEGATEE_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS_DATA[0].account


async def test_delegations_set_use_vests(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    operation = DelegateVestingSharesOperation(
        delegator=WORKING_ACCOUNT_DATA.account.name,
        delegatee=DELEGATEE_ACCOUNT.name,
        vesting_shares=AMOUNT_TO_DELEGATE1,
    )

    # ACT
    result = cli_tester.process_delegations_set(
        delegatee=operation.delegatee,
        amount=AMOUNT_TO_DELEGATE1,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_delegations_set_use_hive(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.process_delegations_set(
        delegatee=DELEGATEE_ACCOUNT.name,
        amount=AMOUNT_TO_DELEGATE3,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_transaction_in_blockchain(node, result)


async def test_delegations_reset(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_delegations_set(
        delegatee=DELEGATEE_ACCOUNT.name,
        amount=AMOUNT_TO_DELEGATE1,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )
    operation = DelegateVestingSharesOperation(
        delegator=WORKING_ACCOUNT_DATA.account.name,
        delegatee=DELEGATEE_ACCOUNT.name,
        vesting_shares=AMOUNT_TO_DELEGATE2,
    )

    # ACT
    result = cli_tester.process_delegations_set(
        delegatee=operation.delegatee,
        amount=AMOUNT_TO_DELEGATE2,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_delegations_remove(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_delegations_set(
        delegatee=DELEGATEE_ACCOUNT.name,
        amount=AMOUNT_TO_DELEGATE1,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )
    operation = DelegateVestingSharesOperation(
        delegator=WORKING_ACCOUNT_DATA.account.name,
        delegatee=DELEGATEE_ACCOUNT.name,
        vesting_shares=Asset.vests(VESTS_TO_REMOVE_DELEGATION),
    )

    # ACT
    result = cli_tester.process_delegations_remove(
        delegatee=operation.delegatee, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)
    assert_no_delegations(cli_tester)
