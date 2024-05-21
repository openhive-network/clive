from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive_local_tools.cli.checkers import assert_no_withdraw_routes, assert_withdraw_routes
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.cli.cli_tester import CLITester


WITHDRAW_TO_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS_DATA[0].account
PERCENT1: int = 12
PERCENT2: int = 30


async def test_withdraw_routes_set(cli_tester: CLITester) -> None:
    # ACT
    cli_tester.process_withdraw_routes_set(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, to=WITHDRAW_TO_ACCOUNT.name, percent=PERCENT1
    )

    # ASSERT
    assert_withdraw_routes(cli_tester, to=WITHDRAW_TO_ACCOUNT.name, percent=PERCENT1)


@pytest.mark.parametrize("auto_vest", [True, False])
async def test_withdraw_routes_set_autovest(cli_tester: CLITester, auto_vest: bool) -> None:  # noqa: FBT001
    # ACT
    cli_tester.process_withdraw_routes_set(
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        to=WITHDRAW_TO_ACCOUNT.name,
        percent=PERCENT1,
        auto_vest=auto_vest,
    )

    # ASSERT
    assert_withdraw_routes(cli_tester, to=WITHDRAW_TO_ACCOUNT.name, percent=PERCENT1, auto_vest=auto_vest)


async def test_withdraw_routes_reset(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_withdraw_routes_set(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, to=WITHDRAW_TO_ACCOUNT.name, percent=PERCENT1
    )

    # ACT
    cli_tester.process_withdraw_routes_set(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, to=WITHDRAW_TO_ACCOUNT.name, percent=PERCENT2
    )

    # ASSERT
    assert_withdraw_routes(cli_tester, to=WITHDRAW_TO_ACCOUNT.name, percent=PERCENT2)


async def test_withdraw_routes_remove(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_withdraw_routes_set(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, to=WITHDRAW_TO_ACCOUNT.name, percent=PERCENT1
    )

    # ACT
    cli_tester.process_withdraw_routes_remove(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, to=WITHDRAW_TO_ACCOUNT.name
    )

    # ASSERT
    assert_no_withdraw_routes(cli_tester)
