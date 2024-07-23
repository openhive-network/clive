from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest
import test_tools as tt

from clive.__private.core.constants.node import VALUE_TO_REMOVE_SCHEDULED_TRANSFER
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.cli.helpers import get_prepared_recurrent_transfer_operation
from clive_local_tools.data.constants import (
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)
from clive_local_tools.testnet_block_log import WORKING_ACCOUNT_DATA
from clive_local_tools.testnet_block_log.constants import ALT_WORKING_ACCOUNT1_DATA

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


from clive_local_tools.checkers import assert_operations_placed_in_blockchain, assert_transaction_in_blockchain


@pytest.mark.parametrize("pair_id", [0, 1])
async def test_process_transfer_schedule_remove_simple_coverage(
    node: tt.RawNode,
    cli_tester: CLITester,
    pair_id: int,
) -> None:
    """Check parameters of clive process transfer-schedule remove."""
    # ARRAGE
    account_name = WORKING_ACCOUNT_DATA.account.name
    frequency = "24h"
    memo = "remove memo"
    repeat = 2
    to = ALT_WORKING_ACCOUNT1_DATA.account.name
    result = cli_tester.process_transfer_schedule_create(
        amount=tt.Asset.Hive(1),
        from_=account_name,
        to=to,
        frequency=frequency,
        pair_id=pair_id,
        repeat=repeat,
        memo=memo,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )
    assert_transaction_in_blockchain(node, result)

    # ACT
    result = cli_tester.process_transfer_schedule_remove(
        from_=account_name,
        pair_id=pair_id,
        to=to,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(
        node,
        result,
        get_prepared_recurrent_transfer_operation(
            from_=account_name,
            to=to,
            amount=tt.Asset.Hive(VALUE_TO_REMOVE_SCHEDULED_TRANSFER),
            memo=memo,
            recurrence=frequency,
            pair_id=pair_id,
            executions=repeat,
        ),
    )


async def test_process_transfer_schedule_remove_try_to_remove_not_exsting_scheduled_transfer(
    cli_tester: CLITester,
) -> None:
    """Check for error while trying to remove not existing scheduled transfer."""
    # ARRANGE
    account_name = WORKING_ACCOUNT_DATA.account.name
    to = ALT_WORKING_ACCOUNT1_DATA.account.name
    pair_id = 0
    messages_to_match = [
        f"Scheduled transfer to `{to}` with pair_id `{pair_id}` does not exists.",
        "Please create it first by using `clive process transfer-schedule create` command.",
    ]
    # ACT & ASSERT
    for message_to_match in messages_to_match:
        with pytest.raises(CLITestCommandError, match=re.escape(message_to_match)):
            cli_tester.process_transfer_schedule_remove(
                from_=account_name,
                to=to,
                pair_id=pair_id,
                password=WORKING_ACCOUNT_PASSWORD,
                sign=WORKING_ACCOUNT_KEY_ALIAS,
            )


async def test_process_transfer_schedule_remove_invalid_pair_id_value(
    cli_tester: CLITester,
) -> None:
    """Check for error while passing invalid pair_id value."""
    # ARRANGE
    account_name = WORKING_ACCOUNT_DATA.account.name
    pair_id_invalid_value = -1
    # ACT & ASSERT
    with pytest.raises(
        CLITestCommandError,
        match="Invalid value for '--pair-id': -1 is not in the range x>=0.",
    ):
        cli_tester.process_transfer_schedule_remove(
            from_=account_name,
            to=ALT_WORKING_ACCOUNT1_DATA.account.name,
            pair_id=pair_id_invalid_value,
            password=WORKING_ACCOUNT_PASSWORD,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
        )
