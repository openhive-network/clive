from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.core.constants.node import PERCENT_TO_REMOVE_WITHDRAW_ROUTE
from clive.__private.core.percent_conversions import percent_to_hive_percent
from clive_local_tools.checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.checkers import assert_no_withdraw_routes
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA
from schemas.operations import SetWithdrawVestingRouteOperation

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.cli.cli_tester import CLITester


WITHDRAW_TO_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS_DATA[0].account
PERCENT1: int = 12
PERCENT2: int = 30


async def test_withdraw_routes_set(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    operation = SetWithdrawVestingRouteOperation(
        from_account=WORKING_ACCOUNT_DATA.account.name,
        to_account=WITHDRAW_TO_ACCOUNT.name,
        percent=percent_to_hive_percent(Decimal(PERCENT1)),
        auto_vest=False,
    )

    # ACT
    result = cli_tester.process_withdraw_routes_set(
        to=operation.to_account, percent=PERCENT1, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


@pytest.mark.parametrize("auto_vest", [True, False])
async def test_withdraw_routes_set_autovest(node: tt.RawNode, cli_tester: CLITester, auto_vest: bool) -> None:  # noqa: FBT001
    # ARRANGE
    operation = SetWithdrawVestingRouteOperation(
        from_account=WORKING_ACCOUNT_DATA.account.name,
        to_account=WITHDRAW_TO_ACCOUNT.name,
        percent=percent_to_hive_percent(Decimal(PERCENT1)),
        auto_vest=auto_vest,
    )

    # ACT
    result = cli_tester.process_withdraw_routes_set(
        to=operation.to_account,
        percent=PERCENT1,
        auto_vest=operation.auto_vest,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_withdraw_routes_reset(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_withdraw_routes_set(
        to=WITHDRAW_TO_ACCOUNT.name, percent=PERCENT1, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )
    operation = SetWithdrawVestingRouteOperation(
        from_account=WORKING_ACCOUNT_DATA.account.name,
        to_account=WITHDRAW_TO_ACCOUNT.name,
        percent=percent_to_hive_percent(Decimal(PERCENT2)),
        auto_vest=False,
    )

    # ACT
    result = cli_tester.process_withdraw_routes_set(
        to=operation.to_account, percent=PERCENT2, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_withdraw_routes_remove(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_withdraw_routes_set(
        to=WITHDRAW_TO_ACCOUNT.name, percent=PERCENT1, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )
    operation = SetWithdrawVestingRouteOperation(
        from_account=WORKING_ACCOUNT_DATA.account.name,
        to_account=WITHDRAW_TO_ACCOUNT.name,
        percent=percent_to_hive_percent(Decimal(PERCENT_TO_REMOVE_WITHDRAW_ROUTE)),
        auto_vest=False,
    )

    # ACT
    result = cli_tester.process_withdraw_routes_remove(
        to=operation.to_account, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)
    assert_no_withdraw_routes(cli_tester)
