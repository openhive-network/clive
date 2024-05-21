from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive_local_tools.cli.checkers import (
    assert_no_delegations,
    assert_no_withdraw_routes,
    assert_withdraw_routes,
)
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import EMPTY_ACCOUNT, WATCHED_ACCOUNTS_DATA

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


OTHER_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS_DATA[0].account
ZERO_HIVE: Final[tt.Asset.HiveT] = tt.Asset.Test(0)
ZERO_VESTS: Final[tt.Asset.VestT] = tt.Asset.Vest(0)
AMOUNT_TO_POWER_UP: Final[tt.Asset.HiveT] = tt.Asset.Test(234.567)
AMOUNT_TO_POWER_DOWN: Final[tt.Asset.VestT] = tt.Asset.Vest(345.678)
AMOUNT_TO_DELEGATE: Final[tt.Asset.VestT] = tt.Asset.Vest(123_456.789)
WITHDRAW_ROUTE_PERCENT: Final[int] = 13


async def test_hive_power_empty_account(cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.show_hive_power(account_name=EMPTY_ACCOUNT.name)

    # ASSERT
    assert_no_delegations(result)
    assert_no_withdraw_routes(result)


async def test_hive_power_effective(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_power_up(
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        amount=AMOUNT_TO_POWER_UP,
        to=EMPTY_ACCOUNT.name,
    )

    # ACT
    cli_tester.show_hive_power(account_name=EMPTY_ACCOUNT.name)


async def test_hive_power_power_down(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_power_down_restart(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, amount=AMOUNT_TO_POWER_DOWN
    )

    # ACT
    cli_tester.show_hive_power()


async def test_hive_power_delegations(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_delegations_set(
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        delegatee=EMPTY_ACCOUNT.name,
        amount=AMOUNT_TO_DELEGATE,
    )

    # ACT
    cli_tester.show_hive_power()


async def test_hive_power_withdraw_routes(cli_tester: CLITester) -> None:
    # ACT
    cli_tester.process_withdraw_routes_set(
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        to=EMPTY_ACCOUNT.name,
        percent=WITHDRAW_ROUTE_PERCENT,
    )

    # ASSERT
    assert_withdraw_routes(cli_tester, to=EMPTY_ACCOUNT.name, percent=WITHDRAW_ROUTE_PERCENT)


async def test_hive_power_withdraw_routes_auto_vest(cli_tester: CLITester) -> None:
    # ACT
    cli_tester.process_withdraw_routes_set(
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        to=EMPTY_ACCOUNT.name,
        percent=WITHDRAW_ROUTE_PERCENT,
        auto_vest=True,
    )

    # ASSERT
    assert_withdraw_routes(cli_tester, to=EMPTY_ACCOUNT.name, percent=WITHDRAW_ROUTE_PERCENT, auto_vest=True)
