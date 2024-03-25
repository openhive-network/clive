from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive_local_tools.cli.checkers import assert_no_withdraw_routes, assert_withdraw_routes
from clive_local_tools.data.constants import (
    WATCHED_ACCOUNTS,
    WORKING_ACCOUNT,
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester
    from schemas.fields.basic import PublicKey


WITHDRAW_TO_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS[0]
PERCENT: int = 12


async def test_withdraw_routes_set(cli_tester: CLITester) -> None:
    # ACT
    cli_tester.process_withdraw_routes_set(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, to=WITHDRAW_TO_ACCOUNT.name, percent=PERCENT
    )

    # ASSERT
    assert_withdraw_routes(cli_tester, to=WITHDRAW_TO_ACCOUNT.name, percent=PERCENT)


async def test_withdraw_routes_remove(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_withdraw_routes_set(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, to=WITHDRAW_TO_ACCOUNT.name, percent=PERCENT
    )

    # ACT
    cli_tester.process_withdraw_routes_remove(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, to=WITHDRAW_TO_ACCOUNT.name
    )

    # ASSERT
    assert_no_withdraw_routes(cli_tester)
