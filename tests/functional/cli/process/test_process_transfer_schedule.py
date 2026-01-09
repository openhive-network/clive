from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

import test_tools as tt

from clive.__private.cli.common.parsers import scheduled_transfer_frequency_parser
from clive.__private.cli.exceptions import (
    ProcessTransferScheduleAlreadyExistsError,
    ProcessTransferScheduleNullPairIdError,
)
from clive.__private.core.constants.node_special_assets import SCHEDULED_TRANSFER_REMOVE_ASSETS
from clive.__private.core.date_utils import timedelta_to_int_hours
from clive.__private.models.schemas import RecurrentTransferOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import get_formatted_error_message
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
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
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
    modified_repeat = 2  # can't be 1 because of a known issue: https://gitlab.syncad.com/hive/hive/-/issues/786
    operation = RecurrentTransferOperation(
        from_=ACCOUNT_NAME, to=RECEIVER, amount=AMOUNT, memo=modified_memo, recurrence=RECURRENCE, executions=REPEAT
    )

    cli_tester.process_transfer_schedule_create(
        from_=ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        repeat=REPEAT,
        frequency=FREQUENCY,
    )

    # ACT
    result = cli_tester.process_transfer_schedule_modify(
        to=RECEIVER, repeat=modified_repeat, memo=modified_memo, sign_with=WORKING_ACCOUNT_KEY_ALIAS
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
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        repeat=REPEAT,
        frequency=FREQUENCY,
    )

    # ACT
    result = cli_tester.process_transfer_schedule_remove(to=RECEIVER, sign_with=WORKING_ACCOUNT_KEY_ALIAS)

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_modify_without_pair_id_when_single_transfer_has_nonzero_pair_id(cli_tester: CLITester) -> None:
    # ARRANGE
    nonzero_pair_id = 5
    cli_tester.process_transfer_schedule_create(
        from_=ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        repeat=REPEAT,
        frequency=FREQUENCY,
        pair_id=nonzero_pair_id,
    )
    expected_error = get_formatted_error_message(
        ProcessTransferScheduleNullPairIdError(RECEIVER, existing_pair_id=nonzero_pair_id)
    )

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_transfer_schedule_modify(to=RECEIVER, memo="modified", sign_with=WORKING_ACCOUNT_KEY_ALIAS)


async def test_modify_without_pair_id_when_multiple_transfers_exist(cli_tester: CLITester) -> None:
    # ARRANGE - create two transfers to same receiver with different pair_ids
    cli_tester.process_transfer_schedule_create(
        from_=ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        repeat=REPEAT,
        frequency=FREQUENCY,
        pair_id=0,
    )
    cli_tester.process_transfer_schedule_create(
        from_=ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        repeat=REPEAT,
        frequency=FREQUENCY,
        pair_id=1,
    )
    expected_error = get_formatted_error_message(ProcessTransferScheduleNullPairIdError(RECEIVER))

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_transfer_schedule_modify(to=RECEIVER, memo="modified", sign_with=WORKING_ACCOUNT_KEY_ALIAS)


async def test_remove_without_pair_id_when_single_transfer_has_nonzero_pair_id(cli_tester: CLITester) -> None:
    # ARRANGE
    nonzero_pair_id = 5
    cli_tester.process_transfer_schedule_create(
        from_=ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        repeat=REPEAT,
        frequency=FREQUENCY,
        pair_id=nonzero_pair_id,
    )
    expected_error = get_formatted_error_message(
        ProcessTransferScheduleNullPairIdError(RECEIVER, existing_pair_id=nonzero_pair_id)
    )

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_transfer_schedule_remove(to=RECEIVER, sign_with=WORKING_ACCOUNT_KEY_ALIAS)


async def test_remove_without_pair_id_when_multiple_transfers_exist(cli_tester: CLITester) -> None:
    # ARRANGE - create two transfers to same receiver with different pair_ids
    cli_tester.process_transfer_schedule_create(
        from_=ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        repeat=REPEAT,
        frequency=FREQUENCY,
        pair_id=0,
    )
    cli_tester.process_transfer_schedule_create(
        from_=ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        repeat=REPEAT,
        frequency=FREQUENCY,
        pair_id=1,
    )
    expected_error = get_formatted_error_message(ProcessTransferScheduleNullPairIdError(RECEIVER))

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_transfer_schedule_remove(to=RECEIVER, sign_with=WORKING_ACCOUNT_KEY_ALIAS)


async def test_create_without_pair_id_when_transfer_with_pair_id_zero_exists(cli_tester: CLITester) -> None:
    # ARRANGE - create first transfer with default pair_id=0
    cli_tester.process_transfer_schedule_create(
        from_=ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        repeat=REPEAT,
        frequency=FREQUENCY,
    )
    expected_error = get_formatted_error_message(ProcessTransferScheduleAlreadyExistsError(RECEIVER, pair_id=0))

    # ACT & ASSERT - try to create second transfer without specifying pair_id
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_transfer_schedule_create(
            from_=ACCOUNT_NAME,
            to=RECEIVER,
            amount=AMOUNT,
            memo="second transfer",
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
            repeat=REPEAT,
            frequency=FREQUENCY,
        )
