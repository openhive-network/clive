from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive_local_tools.cli.checkers import assert_no_pending_power_down
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import EMPTY_ACCOUNT

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT_TO_POWER_DOWN: Final[tt.Asset.VestT] = tt.Asset.Vest(345.678)
SINGLE_POWER_DOWN: Final[tt.Asset.VestT] = AMOUNT_TO_POWER_DOWN / 13


async def test_no_pending_power_down(cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.show_pending_power_down(account_name=EMPTY_ACCOUNT.name)

    # ASSERT
    assert_no_pending_power_down(result)


async def test_pending_power_down_basic(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_power_down_restart(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, amount=AMOUNT_TO_POWER_DOWN
    )

    # ACT
    cli_tester.show_pending_power_down(account_name=EMPTY_ACCOUNT.name)
