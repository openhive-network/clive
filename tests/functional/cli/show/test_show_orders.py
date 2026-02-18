from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

HIVE_AMOUNT: Final[tt.Asset.TestT] = tt.Asset.Test(100)
HBD_AMOUNT: Final[tt.Asset.TbdT] = tt.Asset.Tbd(25)


async def test_show_orders(
    cli_tester: CLITester,
) -> None:
    """Test clive show orders command."""
    # ARRANGE - create an order first
    order_id = 20

    cli_tester.process_order_create(
        from_=WORKING_ACCOUNT_NAME,
        amount_to_sell=HIVE_AMOUNT,
        min_to_receive=HBD_AMOUNT,
        order_id=order_id,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ACT
    result = cli_tester.show_orders(account_name=WORKING_ACCOUNT_NAME)

    # ASSERT
    assert result.exit_code == 0
    output = result.output.lower()

    # Check that the table contains expected column headers
    assert "sell" in output
    assert "receive" in output
    assert "hbd/hive" in output
    assert "created" in output
    assert "expires" in output

    # Check that order values are displayed (100.000 TESTS and 25.000 TBD)
    assert "100.000" in result.output
    assert "25.000" in result.output
    assert str(order_id) in result.output


async def test_show_orders_empty(
    cli_tester: CLITester,
) -> None:
    """Test clive show orders command when no orders exist."""
    # ARRANGE - use an account that has no orders
    account_with_no_orders = WATCHED_ACCOUNTS_DATA[2].account.name  # john

    # ACT
    result = cli_tester.show_orders(account_name=account_with_no_orders)

    # ASSERT
    assert result.exit_code == 0
    # Should show a message about no orders
    output = result.output.lower()
    assert "no" in output
    assert "order" in output
