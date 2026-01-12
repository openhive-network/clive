from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive.__private.cli.common.parsers import scheduled_transfer_frequency_parser
from clive.__private.core.constants.node_special_assets import SCHEDULED_TRANSFER_REMOVE_ASSETS
from clive.__private.core.date_utils import timedelta_to_int_hours
from clive.__private.models.schemas import RecurrentTransferOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import get_operation_from_transaction, get_transaction_id_from_output
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_NAMES, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

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


async def test_creation_with_encrypted_memo(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Check that transfer-schedule create encrypts memo when it starts with '#'."""
    # ARRANGE
    memo_content = "#This is a secret scheduled transfer memo"

    # ACT
    result = cli_tester.process_transfer_schedule_create(
        from_=ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        repeat=REPEAT,
        frequency=FREQUENCY,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=memo_content,
    )

    # ASSERT
    assert result.exit_code == 0

    transaction_id = get_transaction_id_from_output(result.stdout)
    op = get_operation_from_transaction(node, transaction_id, RecurrentTransferOperation)
    assert op.memo.startswith("#"), "Encrypted memos start with '#' followed by the encoded key data"
    assert len(op.memo) > len(memo_content), "The encrypted memo should be longer than the original"


async def test_modification_keeps_encrypted_memo_when_not_modified(node: tt.RawNode, cli_tester: CLITester) -> None:
    """
    Check that modifying a transfer schedule without providing memo keeps the original encrypted memo.

    When memo was previously encrypted during create and modify doesn't provide a new memo,
    the original encrypted memo should be preserved as-is without re-encryption.
    """
    # ARRANGE
    memo_content = "#Original secret memo"
    cli_tester.process_transfer_schedule_create(
        from_=ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        repeat=10,
        frequency=FREQUENCY,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=memo_content,
    )

    # Get the actual encrypted memo from the blockchain
    node.wait_number_of_blocks(1)
    recurrent_transfers = node.api.database.find_recurrent_transfers(from_=ACCOUNT_NAME)
    assert recurrent_transfers.recurrent_transfers, "Recurrent transfer should exist"
    original_encrypted_memo = recurrent_transfers.recurrent_transfers[0].memo

    # ACT - modify only the amount, not the memo
    result = cli_tester.process_transfer_schedule_modify(
        from_=ACCOUNT_NAME,
        to=RECEIVER,
        amount=tt.Asset.Hive(2),
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert result.exit_code == 0

    transaction_id = get_transaction_id_from_output(result.stdout)
    op = get_operation_from_transaction(node, transaction_id, RecurrentTransferOperation)
    assert op.memo == original_encrypted_memo, (
        "When memo is not modified, the original encrypted memo should be preserved exactly"
    )


async def test_modification_with_new_plain_memo(node: tt.RawNode, cli_tester: CLITester) -> None:
    """
    Check that modifying a transfer schedule with a new plain memo works correctly.

    When a new memo is provided that doesn't start with '#', it should be used as-is.
    """
    # ARRANGE
    cli_tester.process_transfer_schedule_create(
        from_=ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        repeat=10,
        frequency=FREQUENCY,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo="Original plain memo",
    )
    new_memo = "New plain memo content"

    # ACT
    result = cli_tester.process_transfer_schedule_modify(
        from_=ACCOUNT_NAME,
        to=RECEIVER,
        memo=new_memo,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert result.exit_code == 0

    transaction_id = get_transaction_id_from_output(result.stdout)
    op = get_operation_from_transaction(node, transaction_id, RecurrentTransferOperation)
    assert op.memo == new_memo, "Plain memo should be stored as-is"


async def test_modification_with_new_encrypted_memo(node: tt.RawNode, cli_tester: CLITester) -> None:
    """
    Check that modifying a transfer schedule with a new encrypted memo encrypts it.

    When a new memo starting with '#' is provided, it should be encrypted.
    """
    # ARRANGE
    cli_tester.process_transfer_schedule_create(
        from_=ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        repeat=10,
        frequency=FREQUENCY,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo="Original plain memo",
    )
    new_memo = "#New secret memo to encrypt"

    # ACT
    result = cli_tester.process_transfer_schedule_modify(
        from_=ACCOUNT_NAME,
        to=RECEIVER,
        memo=new_memo,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert result.exit_code == 0

    transaction_id = get_transaction_id_from_output(result.stdout)
    op = get_operation_from_transaction(node, transaction_id, RecurrentTransferOperation)
    assert op.memo.startswith("#"), "Encrypted memos start with '#' followed by the encoded key data"
    assert len(op.memo) > len(new_memo), "The encrypted memo should be longer than the original"
