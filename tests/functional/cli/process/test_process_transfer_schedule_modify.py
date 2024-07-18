from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest
import test_tools as tt

from clive.__private.core.constants.node import (
    HIVE_MAX_RECURRENT_TRANSFER_END_DATE_DAYS,
    SCHEDULED_TRANSFER_MAX_LIFETIME,
    VALUE_TO_REMOVE_SCHEDULED_TRANSFER,
)
from clive.__private.core.formatters.humanize import humanize_timedelta
from clive.__private.core.shorthand_timedelta import shorthand_timedelta_to_timedelta
from clive.__private.validators.scheduled_transfer_frequency_value_validator import ScheduledTransferFrequencyValidator
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


@pytest.mark.parametrize("to", [ALT_WORKING_ACCOUNT1_DATA.account.name])
@pytest.mark.parametrize("amount", [tt.Asset.Hive(10), tt.Asset.Hbd(10)])
@pytest.mark.parametrize("frequency", ["24h", "1d"])
@pytest.mark.parametrize("pair_id", [0, 1])
@pytest.mark.parametrize("repeat", [5, 10])
@pytest.mark.parametrize("memo", ["memo1", "memo2"])
async def test_process_transfer_schedule_modify_simple_coverage(  # noqa: PLR0913
    node: tt.RawNode,
    cli_tester: CLITester,
    to: str,
    amount: tt.Asset.HiveT | tt.Asset.HbdT,
    frequency: str,
    pair_id: int,
    repeat: int,
    memo: str,
) -> None:
    """Check values of scheduled transfer definitions and upcoming scheduled transfers after modification."""
    # ARRAGE
    account_name = WORKING_ACCOUNT_DATA.account.name
    result = cli_tester.process_transfer_schedule_create(
        amount=tt.Asset.Hive(1),
        from_=account_name,
        to=to,
        frequency="1w",
        pair_id=pair_id,
        repeat=2,
        memo="start memo",
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )
    assert_transaction_in_blockchain(node, result)

    # ACT
    result = cli_tester.process_transfer_schedule_modify(
        amount=amount,
        from_=account_name,
        pair_id=pair_id,
        to=to,
        frequency=frequency,
        repeat=repeat,
        memo=memo,
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
            amount=amount,
            memo=memo,
            recurrence=frequency,
            executions=repeat,
            pair_id=pair_id,
        ),
    )


async def test_process_transfer_schedule_modify_try_to_modify_not_exsting_scheduled_transfer(
    cli_tester: CLITester,
) -> None:
    """Check for error while trying to mofidy not existing scheduled transfer."""
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
            cli_tester.process_transfer_schedule_modify(
                amount=tt.Asset.Hive(1),
                from_=account_name,
                to=to,
                frequency="24h",
                pair_id=pair_id,
                repeat=2,
                memo="some memo",
                password=WORKING_ACCOUNT_PASSWORD,
                sign=WORKING_ACCOUNT_KEY_ALIAS,
            )


@pytest.mark.parametrize(
    ("frequency", "repeat"),
    [
        ("1d", HIVE_MAX_RECURRENT_TRANSFER_END_DATE_DAYS + 1),
        ("366d", 2),
        (None, HIVE_MAX_RECURRENT_TRANSFER_END_DATE_DAYS + 1),
        (str(HIVE_MAX_RECURRENT_TRANSFER_END_DATE_DAYS + 1) + "d", None),
    ],
)
async def test_process_transfer_schedule_modify_lifetime_too_greate(
    cli_tester: CLITester,
    frequency: str,
    repeat: int,
) -> None:
    """
    Check for error while passing values for combination of repeat and frequency.

    It will try to create scheduled transfer with lifetime greater than SCHEDULED_TRANSFER_MAX_LIFETIME
    """
    # ARRANGE
    account_name = WORKING_ACCOUNT_DATA.account.name
    frequency_create = "24h"
    repeat_create = 2
    cli_tester.process_transfer_schedule_create(
        amount=tt.Asset.Hive(1),
        from_=account_name,
        to=ALT_WORKING_ACCOUNT1_DATA.account.name,
        frequency=frequency_create,
        pair_id=0,
        repeat=repeat_create,
        memo="some memo",
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    if repeat is None:
        requested_lifetime = shorthand_timedelta_to_timedelta(frequency) * repeat_create
    elif frequency is None:
        requested_lifetime = shorthand_timedelta_to_timedelta(frequency_create) * repeat
    else:
        requested_lifetime = shorthand_timedelta_to_timedelta(frequency) * repeat
    messages_to_match = [
        f"Requested lifetime of scheduled transfer is too long ({humanize_timedelta(requested_lifetime)}).",
        f"Maximum available lifetime is {humanize_timedelta(SCHEDULED_TRANSFER_MAX_LIFETIME)}",
    ]

    # ACT & ASSERT
    for message_to_match in messages_to_match:
        with pytest.raises(CLITestCommandError, match=re.escape(message_to_match)):
            cli_tester.process_transfer_schedule_modify(
                amount=tt.Asset.Hive(1),
                from_=account_name,
                to=ALT_WORKING_ACCOUNT1_DATA.account.name,
                frequency=frequency,
                pair_id=0,
                repeat=repeat,
                memo="some memo",
                password=WORKING_ACCOUNT_PASSWORD,
                sign=WORKING_ACCOUNT_KEY_ALIAS,
            )


@pytest.mark.parametrize(
    "invalid_remove_amount",
    [
        tt.Asset.Hive(VALUE_TO_REMOVE_SCHEDULED_TRANSFER),
        tt.Asset.Hbd(VALUE_TO_REMOVE_SCHEDULED_TRANSFER),
    ],
)
async def test_process_transfer_schedule_modify_invalid_remove_amount(
    cli_tester: CLITester,
    invalid_remove_amount: tt.Asset.HiveT | tt.Asset.HbdT,
) -> None:
    """Check for error while passing remove value to amount."""
    # ARRANGE
    account_name = WORKING_ACCOUNT_DATA.account.name
    hive_symbol = tt.Asset.Hive(1).get_asset_information().get_symbol()
    hbd_symbol = tt.Asset.Hbd(1).get_asset_information().get_symbol()
    messages_to_match = [
        (
            "Amount for `clive process transfer-schedule create` or `clive process transfer-schedule modify` "
            f"commands must be greater than {VALUE_TO_REMOVE_SCHEDULED_TRANSFER}"
        ),
        f"{hive_symbol}/{hbd_symbol}.",
        "If you want to remove scheduled transfer, please use `clive process transfer-schedule remove` command.",
    ]
    cli_tester.process_transfer_schedule_create(
        amount=tt.Asset.Hive(1),
        from_=account_name,
        to=ALT_WORKING_ACCOUNT1_DATA.account.name,
        frequency="24h",
        pair_id=0,
        repeat=2,
        memo="some memo",
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ACT & ASSERT
    for message_to_match in messages_to_match:
        with pytest.raises(CLITestCommandError, match=re.escape(message_to_match)):
            cli_tester.process_transfer_schedule_modify(
                amount=invalid_remove_amount,
                from_=account_name,
                to=ALT_WORKING_ACCOUNT1_DATA.account.name,
                frequency="1d",
                pair_id=0,
                repeat=2,
                memo="some memo",
                password=WORKING_ACCOUNT_PASSWORD,
                sign=WORKING_ACCOUNT_KEY_ALIAS,
            )


async def test_process_transfer_schedule_modify_invalid_repeat_value(
    cli_tester: CLITester,
) -> None:
    """Check for error while passing repeat value too small."""
    # ARRANGE
    account_name = WORKING_ACCOUNT_DATA.account.name
    repeat_invalid_value = 1
    # ACT & ASSERT
    with pytest.raises(
        CLITestCommandError,
        match="Invalid value for '--repeat': 1 is not in the range x>=2.",
    ):
        cli_tester.process_transfer_schedule_modify(
            amount=tt.Asset.Hive(1),
            from_=account_name,
            to=ALT_WORKING_ACCOUNT1_DATA.account.name,
            frequency="24h",
            pair_id=0,
            repeat=repeat_invalid_value,
            memo="some memo",
            password=WORKING_ACCOUNT_PASSWORD,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_process_transfer_schedule_modify_invalid_frequency_value(
    cli_tester: CLITester,
) -> None:
    """Check for error while passing frequency value too small."""
    # ARRANGE
    account_name = WORKING_ACCOUNT_DATA.account.name
    frequency_invalid_value = "23h"
    # ACT & ASSERT
    with pytest.raises(
        CLITestCommandError,
        match=ScheduledTransferFrequencyValidator.VALUE_TO_SMALL_DESCRIPTION,
    ):
        cli_tester.process_transfer_schedule_modify(
            amount=tt.Asset.Hive(1),
            from_=account_name,
            to=ALT_WORKING_ACCOUNT1_DATA.account.name,
            frequency=frequency_invalid_value,
            pair_id=0,
            repeat=2,
            memo="some memo",
            password=WORKING_ACCOUNT_PASSWORD,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_process_transfer_schedule_modify_invalid_pair_id_value(
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
        cli_tester.process_transfer_schedule_modify(
            amount=tt.Asset.Hive(1),
            from_=account_name,
            to=ALT_WORKING_ACCOUNT1_DATA.account.name,
            frequency="24h",
            pair_id=pair_id_invalid_value,
            repeat=2,
            memo="some memo",
            password=WORKING_ACCOUNT_PASSWORD,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
        )
