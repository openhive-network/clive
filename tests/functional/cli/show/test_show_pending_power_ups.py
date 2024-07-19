from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive_local_tools.cli.checkers import assert_no_pending_power_ups
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import EMPTY_ACCOUNT

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT_TO_POWER_UP: Final[tt.Asset.HiveT] = tt.Asset.Test(234.567)


async def test_no_pending_power_ups(cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.show_pending_power_ups(account_name=EMPTY_ACCOUNT.name)

    # ASSERT
    assert_no_pending_power_ups(result)


async def test_pending_power_ups_basic(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_power_up(
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        amount=AMOUNT_TO_POWER_UP,
        to=EMPTY_ACCOUNT.name,
    )

    # ACT
    cli_tester.show_pending_power_ups(account_name=EMPTY_ACCOUNT.name)


async def test_pending_power_ups_default_account(cli_tester: CLITester) -> None:
    # ACT
    cli_tester.show_pending_power_ups()
