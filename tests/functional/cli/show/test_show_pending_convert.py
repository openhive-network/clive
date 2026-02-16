from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log import EMPTY_ACCOUNT, WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT_HBD: Final[tt.Asset.HbdT] = tt.Asset.Hbd(10.000)
AMOUNT_HIVE: Final[tt.Asset.HiveT] = tt.Asset.Hive(10.000)


async def test_show_pending_convert_none(cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.show_pending_convert(account_name=EMPTY_ACCOUNT.name)

    # ASSERT
    assert "no pending conversions" in result.stdout, "There should be no pending conversions."


async def test_show_pending_convert_hbd(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_convert(amount=AMOUNT_HBD, sign_with=WORKING_ACCOUNT_KEY_ALIAS)

    # ACT
    result = cli_tester.show_pending_convert(account_name=WORKING_ACCOUNT_DATA.account.name)

    # ASSERT
    assert "HBD → HIVE" in result.stdout, "Should show HBD to HIVE conversion table."
    assert AMOUNT_HBD.pretty_amount() in result.stdout, f"Should show amount {AMOUNT_HBD.pretty_amount()}."


async def test_show_pending_convert_hive(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_convert(amount=AMOUNT_HIVE, sign_with=WORKING_ACCOUNT_KEY_ALIAS)

    # ACT
    result = cli_tester.show_pending_convert(account_name=WORKING_ACCOUNT_DATA.account.name)

    # ASSERT
    assert "HIVE → HBD" in result.stdout, "Should show HIVE to HBD conversion table."
    assert AMOUNT_HIVE.pretty_amount() in result.stdout, f"Should show amount {AMOUNT_HIVE.pretty_amount()}."
