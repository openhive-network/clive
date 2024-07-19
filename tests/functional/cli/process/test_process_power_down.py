from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.core.constants.node import VESTS_TO_REMOVE_POWER_DOWN
from clive.models.asset import Asset
from clive_local_tools.checkers import assert_operations_placed_in_blockchain, assert_transaction_in_blockchain
from clive_local_tools.cli.checkers import assert_exit_code, assert_no_pending_power_down
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT_DATA
from schemas.operations import WithdrawVestingOperation

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT_TO_POWER_DOWN1: Final[tt.Asset.HiveT] = tt.Asset.Test(123.235)
AMOUNT_TO_POWER_DOWN2: Final[tt.Asset.VestT] = tt.Asset.Vest(345.456)
AMOUNT_TO_POWER_DOWN3: Final[tt.Asset.HiveT] = tt.Asset.Test(234.567)


async def test_power_down_start_success_use_hive(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.process_power_down_start(
        amount=AMOUNT_TO_POWER_DOWN1, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT
    assert_transaction_in_blockchain(node, result)


async def test_power_down_start_success_use_vests(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    operation = WithdrawVestingOperation(
        account=WORKING_ACCOUNT_DATA.account.name,
        vesting_shares=AMOUNT_TO_POWER_DOWN2,
    )

    # ACT
    result = cli_tester.process_power_down_start(
        amount=AMOUNT_TO_POWER_DOWN2,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_power_down_start_fail(cli_tester: CLITester) -> None:
    # ARRNGE
    cli_tester.process_power_down_start(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, amount=AMOUNT_TO_POWER_DOWN1
    )
    expected_error = "Power-down is already in progress"

    # ACT
    with pytest.raises(CLITestCommandError, match=expected_error) as power_down_start_exception_info:
        cli_tester.process_power_down_start(
            amount=AMOUNT_TO_POWER_DOWN3, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
        )

    # ASSERT
    assert_exit_code(power_down_start_exception_info, 1)


async def test_power_down_restart_create_use_hive(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.process_power_down_restart(
        amount=AMOUNT_TO_POWER_DOWN1, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT
    assert_transaction_in_blockchain(node, result)


async def test_power_down_restart_create_use_vests(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    operation = WithdrawVestingOperation(
        account=WORKING_ACCOUNT_DATA.account.name,
        vesting_shares=AMOUNT_TO_POWER_DOWN2,
    )

    # ACT
    result = cli_tester.process_power_down_restart(
        amount=AMOUNT_TO_POWER_DOWN2,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_power_down_restart_override(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_power_down_start(
        amount=AMOUNT_TO_POWER_DOWN1, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )
    operation = WithdrawVestingOperation(
        account=WORKING_ACCOUNT_DATA.account.name,
        vesting_shares=AMOUNT_TO_POWER_DOWN2,
    )

    # ACT
    result = cli_tester.process_power_down_restart(
        amount=AMOUNT_TO_POWER_DOWN2,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_power_down_cancel_success(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_power_down_start(
        amount=AMOUNT_TO_POWER_DOWN1, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )
    operation = WithdrawVestingOperation(
        account=WORKING_ACCOUNT_DATA.account.name,
        vesting_shares=Asset.vests(VESTS_TO_REMOVE_POWER_DOWN),
    )

    # ACT
    result = cli_tester.process_power_down_cancel(password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS)

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)
    assert_no_pending_power_down(cli_tester)


async def test_power_down_cancel_fail(cli_tester: CLITester) -> None:
    # ARRANGE
    expected_error = "network_broadcast_api.broadcast_transaction"

    # ACT
    with pytest.raises(CLITestCommandError, match=expected_error) as power_down_cancel_exception_info:
        cli_tester.process_power_down_cancel(password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS)

    # ASSERT
    assert_exit_code(power_down_cancel_exception_info, 1)
