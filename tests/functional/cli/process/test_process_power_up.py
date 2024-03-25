from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive_local_tools.cli.checkers import assert_memo_key
from clive_local_tools.data.constants import (
    WATCHED_ACCOUNTS,
    WORKING_ACCOUNT,
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester
    from schemas.fields.basic import PublicKey


AMOUNT_TO_POWER_UP: Final[tt.Asset.HiveT] = tt.Asset.Test(654.321)
OTHER_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS[0]


async def test_power_up(cli_tester: CLITester) -> None:
    # ACT
    cli_tester.process_power_up(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, amount=AMOUNT_TO_POWER_UP
    )

    # ASSERT


async def test_power_up_no_default_account(cli_tester: CLITester) -> None:
    # ACT
    cli_tester.process_power_up(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, amount=AMOUNT_TO_POWER_UP,
        from_=WORKING_ACCOUNT.name,
    )

    # ASSERT


async def test_power_up_to_other_account(cli_tester: CLITester) -> None:
    # ACT
    cli_tester.process_power_up(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, amount=AMOUNT_TO_POWER_UP,
        to=OTHER_ACCOUNT.name,
    )

    # ASSERT
    