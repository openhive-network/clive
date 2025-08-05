from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.core.constants.node import PERCENT_TO_REMOVE_WITHDRAW_ROUTE
from clive.__private.core.percent_conversions import percent_to_hive_percent
from clive.__private.models.schemas import SetWithdrawVestingRouteOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.checkers import assert_no_withdraw_routes
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.cli.cli_tester import CLITester


WITHDRAW_TO_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS_DATA[0].account
PERCENT: int = 12


async def test_withdraw_routes_set(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    operation = SetWithdrawVestingRouteOperation(
        from_account=WORKING_ACCOUNT_DATA.account.name,
        to_account=WITHDRAW_TO_ACCOUNT.name,
        percent=percent_to_hive_percent(Decimal(PERCENT)),
        auto_vest=False,
    )

    # ACT
    result = cli_tester.process_withdraw_routes_set(
        to=operation.to_account, percent=PERCENT, sign_with=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


@pytest.mark.parametrize("auto_vest", [True, False])
async def test_withdraw_routes_set_autovest(node: tt.RawNode, cli_tester: CLITester, auto_vest: bool) -> None:  # noqa: FBT001
    # ARRANGE
    operation = SetWithdrawVestingRouteOperation(
        from_account=WORKING_ACCOUNT_DATA.account.name,
        to_account=WITHDRAW_TO_ACCOUNT.name,
        percent=percent_to_hive_percent(Decimal(PERCENT)),
        auto_vest=auto_vest,
    )

    # ACT
    result = cli_tester.process_withdraw_routes_set(
        to=operation.to_account,
        percent=PERCENT,
        auto_vest=operation.auto_vest,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_withdraw_routes_reset(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    percent_reset: int = 30
    cli_tester.process_withdraw_routes_set(
        to=WITHDRAW_TO_ACCOUNT.name, percent=PERCENT, sign_with=WORKING_ACCOUNT_KEY_ALIAS
    )
    operation = SetWithdrawVestingRouteOperation(
        from_account=WORKING_ACCOUNT_DATA.account.name,
        to_account=WITHDRAW_TO_ACCOUNT.name,
        percent=percent_to_hive_percent(Decimal(percent_reset)),
        auto_vest=False,
    )

    # ACT
    result = cli_tester.process_withdraw_routes_set(
        to=operation.to_account,
        percent=percent_reset,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_withdraw_routes_remove(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_withdraw_routes_set(
        to=WITHDRAW_TO_ACCOUNT.name, percent=PERCENT, sign_with=WORKING_ACCOUNT_KEY_ALIAS
    )
    operation = SetWithdrawVestingRouteOperation(
        from_account=WORKING_ACCOUNT_DATA.account.name,
        to_account=WITHDRAW_TO_ACCOUNT.name,
        percent=percent_to_hive_percent(Decimal(PERCENT_TO_REMOVE_WITHDRAW_ROUTE)),
        auto_vest=False,
    )

    # ACT
    result = cli_tester.process_withdraw_routes_remove(to=operation.to_account, sign_with=WORKING_ACCOUNT_KEY_ALIAS)

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)
    assert_no_withdraw_routes(cli_tester)
