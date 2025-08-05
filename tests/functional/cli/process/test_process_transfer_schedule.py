from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

import test_tools as tt

from clive.__private.cli.common.parsers import scheduled_transfer_frequency_parser
from clive.__private.core.constants.node_special_assets import SCHEDULED_TRANSFER_REMOVE_ASSETS
from clive.__private.core.date_utils import timedelta_to_int_hours
from clive.__private.models.schemas import RecurrentTransferOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_NAMES, WORKING_ACCOUNT_NAME

ACCOUNT_NAME: Final[str] = WORKING_ACCOUNT_NAME
RECEIVER: Final[str] = WATCHED_ACCOUNTS_NAMES[0]
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)
MEMO: Final[str] = "test-schedule-transfer"
FREQUENCY: Final[str] = "24h"
RECURRENCE: Final[int] = timedelta_to_int_hours(scheduled_transfer_frequency_parser(FREQUENCY))
REPEAT: Final[int] = 2
OPERATION: RecurrentTransferOperation = RecurrentTransferOperation(
    from_=ACCOUNT_NAME, to=RECEIVER, amount=AMOUNT, memo=MEMO, recurrence=RECURRENCE, executions=REPEAT
)


async def test_creation_of_scheduled_transfer(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    operation = RecurrentTransferOperation(
        from_=ACCOUNT_NAME, to=RECEIVER, amount=AMOUNT, memo=MEMO, recurrence=RECURRENCE, executions=REPEAT
    )

    # ACT
    result = cli_tester.process_transfer_schedule_create(
        from_=ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        repeat=REPEAT,
        frequency=FREQUENCY,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_modification_of_scheduled_transfer(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    # ARRANGE
    modified_memo = "Modified memo"
    operation = RecurrentTransferOperation(
        from_=ACCOUNT_NAME, to=RECEIVER, amount=AMOUNT, memo=modified_memo, recurrence=RECURRENCE, executions=REPEAT
    )

    cli_tester.process_transfer_schedule_create(
        from_=ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        repeat=REPEAT,
        frequency=FREQUENCY,
    )

    # ACT
    result = cli_tester.process_transfer_schedule_modify(
        to=RECEIVER, memo=modified_memo, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_removing_scheduled_transfer(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    # ARRANGE
    operation = RecurrentTransferOperation(
        from_=ACCOUNT_NAME,
        to=RECEIVER,
        amount=SCHEDULED_TRANSFER_REMOVE_ASSETS[0],
        memo=MEMO,
        recurrence=RECURRENCE,
        executions=REPEAT,
    )

    cli_tester.process_transfer_schedule_create(
        from_=ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        repeat=REPEAT,
        frequency=FREQUENCY,
    )

    # ACT
    result = cli_tester.process_transfer_schedule_remove(to=RECEIVER, sign=WORKING_ACCOUNT_KEY_ALIAS)

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)
