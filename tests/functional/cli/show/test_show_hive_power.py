from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive_local_tools.cli.checkers import (
    assert_no_delegations,
    assert_no_withdraw_routes,
    assert_withdraw_routes,
)
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import EMPTY_ACCOUNT

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


WITHDRAW_ROUTE_PERCENT: Final[int] = 13


async def test_hive_power_empty_account(cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.show_hive_power(account_name=EMPTY_ACCOUNT.name)

    # ASSERT
    assert_no_delegations(result)
    assert_no_withdraw_routes(result)


async def test_hive_power_effective(cli_tester: CLITester) -> None:
    # ARRANGE
    amount_to_power_up: Final[tt.Asset.HiveT] = tt.Asset.Hive(234.567)
    cli_tester.process_power_up(sign=WORKING_ACCOUNT_KEY_ALIAS, amount=amount_to_power_up, to=EMPTY_ACCOUNT.name)

    # ACT
    cli_tester.show_hive_power(account_name=EMPTY_ACCOUNT.name)


async def test_hive_power_power_down(cli_tester: CLITester) -> None:
    # ARRANGE
    amount_to_power_down: Final[tt.Asset.VestT] = tt.Asset.Vest(345.678)
    cli_tester.process_power_down_restart(sign=WORKING_ACCOUNT_KEY_ALIAS, amount=amount_to_power_down)

    # ACT
    cli_tester.show_hive_power()


async def test_hive_power_delegations(cli_tester: CLITester) -> None:
    # ARRANGE
    amount_to_delegate: Final[tt.Asset.VestT] = tt.Asset.Vest(123_456.789)
    cli_tester.process_delegations_set(
        sign=WORKING_ACCOUNT_KEY_ALIAS, delegatee=EMPTY_ACCOUNT.name, amount=amount_to_delegate
    )

    # ACT
    cli_tester.show_hive_power()


async def test_hive_power_withdraw_routes(cli_tester: CLITester) -> None:
    # ACT
    cli_tester.process_withdraw_routes_set(
        sign=WORKING_ACCOUNT_KEY_ALIAS, to=EMPTY_ACCOUNT.name, percent=WITHDRAW_ROUTE_PERCENT
    )

    # ASSERT
    assert_withdraw_routes(cli_tester, to=EMPTY_ACCOUNT.name, percent=WITHDRAW_ROUTE_PERCENT)


async def test_hive_power_withdraw_routes_auto_vest(cli_tester: CLITester) -> None:
    # ACT
    cli_tester.process_withdraw_routes_set(
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        to=EMPTY_ACCOUNT.name,
        percent=WITHDRAW_ROUTE_PERCENT,
        auto_vest=True,
    )

    # ASSERT
    assert_withdraw_routes(cli_tester, to=EMPTY_ACCOUNT.name, percent=WITHDRAW_ROUTE_PERCENT, auto_vest=True)
