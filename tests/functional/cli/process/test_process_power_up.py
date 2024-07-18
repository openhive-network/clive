from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive_local_tools.checkers import assert_operations_placed_in_blockchain
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import EMPTY_ACCOUNT, WORKING_ACCOUNT_DATA
from schemas.operations import TransferToVestingOperation

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT_TO_POWER_UP: Final[tt.Asset.HiveT] = tt.Asset.Test(654.321)


async def test_power_up_to_other_account(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    operation = TransferToVestingOperation(
        from_=WORKING_ACCOUNT_DATA.account.name,
        to=EMPTY_ACCOUNT.name,
        amount=AMOUNT_TO_POWER_UP,
    )

    # ACT
    result = cli_tester.process_power_up(
        amount=operation.amount,
        to=operation.to,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_power_up_no_default_account(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    operation = TransferToVestingOperation(
        from_=WORKING_ACCOUNT_DATA.account.name,
        to=EMPTY_ACCOUNT.name,
        amount=AMOUNT_TO_POWER_UP,
    )

    # ACT
    result = cli_tester.process_power_up(
        amount=operation.amount,
        from_=operation.from_,
        to=operation.to,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_power_up_default_account(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    operation = TransferToVestingOperation(
        from_=WORKING_ACCOUNT_DATA.account.name,
        to=WORKING_ACCOUNT_DATA.account.name,
        amount=AMOUNT_TO_POWER_UP,
    )

    # ACT
    result = cli_tester.process_power_up(
        amount=operation.amount,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)
