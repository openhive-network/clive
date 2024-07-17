from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import test_tools as tt

from clive.__private.cli.commands.show.show_transfer_schedule import (
    DEFAULT_UPCOMING_FUTURE_SCHEDULED_TRANSFERS_AMOUNT,
    ERROR_LACK_OF_FUNDS_MESSAGE_RAW,
)
from clive_local_tools.cli.checkers import (
    assert_calculated_possible_balance,
    assert_coverage_scheduled_transfer,
    assert_coverage_upcoming_scheduled_transfer,
    assert_max_number_of_upcoming,
    assert_no_scheduled_transfers_for_account,
    assert_transfers_existing_number,
)
from clive_local_tools.cli.get_data_from_table import (
    get_account_liquid_balance,
    get_data_from_scheduled_transfer_definition_table_for,
    get_data_from_scheduled_transfer_upcoming_table_for,
)
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log import WORKING_ACCOUNT_DATA
from clive_local_tools.testnet_block_log.constants import ALT_WORKING_ACCOUNT1_DATA, ALT_WORKING_ACCOUNT2_DATA

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


async def test_show_transfer_schedule_none(cli_tester: CLITester) -> None:
    """Check proper message for account with no scheduled transfers."""
    # ARRANGE
    account_name = WORKING_ACCOUNT_DATA.account.name

    # ACT
    result = cli_tester.show_transfer_schedule(account_name=account_name)

    # ASSERT
    assert_no_scheduled_transfers_for_account(result.stdout, account_name)


@pytest.mark.parametrize(
    "to",
    [ALT_WORKING_ACCOUNT1_DATA.account.name, ALT_WORKING_ACCOUNT2_DATA.account.name],
)
@pytest.mark.parametrize("amount", [tt.Asset.Hive(10), tt.Asset.Hbd(10)])
@pytest.mark.parametrize("frequency", ["24h", "1d"])
@pytest.mark.parametrize("pair_id", [0, 1])
@pytest.mark.parametrize("repeat", [5, 10])
@pytest.mark.parametrize("memo", ["memo1", "memo2"])
async def test_show_transfer_schedule_create_schedule_simple_coverage(  # noqa: PLR0913
    node: tt.RawNode,
    cli_tester: CLITester,
    to: str,
    amount: tt.Asset.HiveT | tt.Asset.HbdT,
    frequency: str,
    pair_id: int,
    repeat: int,
    memo: str,
) -> None:
    """Check values of scheduled transfer definitions and upcoming scheduled transfers."""
    # ARRAGE
    account_name = WORKING_ACCOUNT_DATA.account.name
    result = cli_tester.process_transfer_schedule_create(
        amount=amount,
        from_=account_name,
        to=to,
        frequency=frequency,
        pair_id=pair_id,
        repeat=repeat,
        memo=memo,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ACT
    node.wait_number_of_blocks(2)
    account_balance_after_scheduled_transfer_creation = get_account_liquid_balance(
        cli_tester, account_name, hive=isinstance(amount, tt.Asset.HiveT)
    )

    result = cli_tester.show_transfer_schedule(account_name=account_name)
    scheduled_transfers = get_data_from_scheduled_transfer_definition_table_for(result.stdout, account_name)
    upcoming_transfers = get_data_from_scheduled_transfer_upcoming_table_for(result.stdout, account_name)

    # ASSERT
    assert_transfers_existing_number(scheduled_transfers, 1, upcoming=False)
    assert_transfers_existing_number(upcoming_transfers, repeat - 1, upcoming=True)
    for scheduled_transfer in scheduled_transfers:
        assert_coverage_scheduled_transfer(
            scheduled_transfer,
            _from=account_name,
            amount=amount,
            frequency=frequency,
            memo=memo,
            pair_id=pair_id,
            remaining=repeat - 1,
            to=to,
        )

    for idx, upcoming_transfer in enumerate(upcoming_transfers, 1):
        assert_coverage_upcoming_scheduled_transfer(
            upcoming_transfer,
            _from=account_name,
            amount=amount,
            possible_amount_after_operation=account_balance_after_scheduled_transfer_creation - idx * amount,
            frequency=frequency,
            pair_id=pair_id,
            to=to,
        )


@pytest.mark.parametrize("amount", [tt.Asset.Hive(20000), tt.Asset.Hbd(20000)])
async def test_show_transfer_schedule_calculations_in_upcoming_table(
    node: tt.RawNode,
    cli_tester: CLITester,
    amount: tt.Asset.HiveT | tt.Asset.HbdT,
) -> None:
    """Check for `possible lack of funds message` in upcoming table."""
    # ARRANGE
    account_name = WORKING_ACCOUNT_DATA.account.name
    result = cli_tester.process_transfer_schedule_create(
        amount=amount,
        from_=account_name,
        to=ALT_WORKING_ACCOUNT1_DATA.account.name,
        frequency="24h",
        pair_id=0,
        repeat=DEFAULT_UPCOMING_FUTURE_SCHEDULED_TRANSFERS_AMOUNT,
        memo="some memo",
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    node.wait_number_of_blocks(2)
    account_balance_after_scheduled_transfer_creation = get_account_liquid_balance(
        cli_tester, account_name, hive=isinstance(amount, tt.Asset.HiveT)
    )

    # ACT
    result = cli_tester.show_transfer_schedule(account_name=account_name)
    scheduled_transfers = get_data_from_scheduled_transfer_definition_table_for(result.stdout, account_name)
    upcoming_transfers = get_data_from_scheduled_transfer_upcoming_table_for(result.stdout, account_name)

    possible_balances: list[tt.Asset.HbdT | tt.Asset.HiveT | str] = []
    calculated_possible_balance = account_balance_after_scheduled_transfer_creation
    for _ in range(DEFAULT_UPCOMING_FUTURE_SCHEDULED_TRANSFERS_AMOUNT):
        if calculated_possible_balance > amount:
            calculated_possible_balance = calculated_possible_balance - amount
            possible_balances.append(calculated_possible_balance)
        else:
            possible_balances.append(ERROR_LACK_OF_FUNDS_MESSAGE_RAW)

    # ASSERT
    assert_transfers_existing_number(scheduled_transfers, 1, upcoming=False)
    assert_transfers_existing_number(upcoming_transfers, 9, upcoming=True)
    for possible_balance, upcoming_transfer in zip(possible_balances, upcoming_transfers):
        assert_calculated_possible_balance(possible_balance, upcoming_transfer)


@pytest.mark.parametrize("amount", [tt.Asset.Hive(10), tt.Asset.Hbd(10)])
async def test_show_transfer_schedule_max_10_incomming_transfers(
    node: tt.RawNode,
    cli_tester: CLITester,
    amount: tt.Asset.HiveT | tt.Asset.HbdT,
) -> None:
    """Check maximum amount of upcoming scheduled transfers."""
    # ARRANGE
    repeat_value_greater_than_max_displayed = DEFAULT_UPCOMING_FUTURE_SCHEDULED_TRANSFERS_AMOUNT + 5
    account_name = WORKING_ACCOUNT_DATA.account.name
    cli_tester.process_transfer_schedule_create(
        amount=amount,
        from_=account_name,
        to=ALT_WORKING_ACCOUNT1_DATA.account.name,
        frequency="24h",
        pair_id=0,
        repeat=repeat_value_greater_than_max_displayed,
        memo="some memo",
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ACT
    node.wait_number_of_blocks(2)
    result = cli_tester.show_transfer_schedule(account_name=account_name)

    # ASSERT
    upcoming_transfers = get_data_from_scheduled_transfer_upcoming_table_for(result.output, account_name)
    assert_max_number_of_upcoming(upcoming_transfers)
