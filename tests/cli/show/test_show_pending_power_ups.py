from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive_local_tools.cli.checkers import assert_no_pending_power_ups
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import EMPTY_ACCOUNT

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


async def test_no_pending_power_ups(cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.show_pending_power_ups(account_name=EMPTY_ACCOUNT.name)

    # ASSERT
    assert_no_pending_power_ups(result)


async def test_pending_power_ups_basic(cli_tester: CLITester) -> None:
    # ARRANGE
    amount_to_power_up: Final[tt.Asset.HiveT] = tt.Asset.Hive(234.567)
    cli_tester.process_power_up(sign=WORKING_ACCOUNT_KEY_ALIAS, amount=amount_to_power_up, to=EMPTY_ACCOUNT.name)

    # ACT
    cli_tester.show_pending_power_ups(account_name=EMPTY_ACCOUNT.name)


async def test_pending_power_ups_default_account(cli_tester: CLITester) -> None:
    # ACT
    cli_tester.show_pending_power_ups()
