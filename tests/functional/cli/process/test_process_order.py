from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import (
    OrderInvalidExpirationError,
    OrderMissingPriceSpecificationError,
    OrderMutuallyExclusiveOptionsError,
    OrderSameAssetError,
)
from clive.__private.models.schemas import LimitOrderCancelOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import get_formatted_error_message
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

HIVE_AMOUNT: Final[tt.Asset.TestT] = tt.Asset.Test(100)
HBD_AMOUNT: Final[tt.Asset.TbdT] = tt.Asset.Tbd(25)


async def test_process_order_create_with_min_to_receive(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test clive process order create with --min-to-receive option."""
    # ARRANGE
    order_id = 1

    # ACT
    result = cli_tester.process_order_create(
        from_=WORKING_ACCOUNT_NAME,
        amount_to_sell=HIVE_AMOUNT,
        min_to_receive=HBD_AMOUNT,
        order_id=order_id,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert result.exit_code == 0


async def test_process_order_create_with_price(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test clive process order create with --price option (auto-calculates min_to_receive)."""
    # ARRANGE
    order_id = 2
    price = Decimal("0.25")  # 0.25 HBD per HIVE

    # ACT
    result = cli_tester.process_order_create(
        from_=WORKING_ACCOUNT_NAME,
        amount_to_sell=HIVE_AMOUNT,
        price=price,
        order_id=order_id,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert result.exit_code == 0


async def test_process_order_create_sell_hive(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test creating an order to sell HIVE for HBD."""
    # ARRANGE
    order_id = 3
    hive_to_sell = tt.Asset.Test(50)
    hbd_to_receive = tt.Asset.Tbd(12.5)

    # ACT
    result = cli_tester.process_order_create(
        from_=WORKING_ACCOUNT_NAME,
        amount_to_sell=hive_to_sell,
        min_to_receive=hbd_to_receive,
        order_id=order_id,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert result.exit_code == 0


async def test_process_order_create_sell_hbd(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test creating an order to sell HBD for HIVE."""
    # ARRANGE
    order_id = 4
    hbd_to_sell = tt.Asset.Tbd(25)
    hive_to_receive = tt.Asset.Test(100)

    # ACT
    result = cli_tester.process_order_create(
        from_=WORKING_ACCOUNT_NAME,
        amount_to_sell=hbd_to_sell,
        min_to_receive=hive_to_receive,
        order_id=order_id,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert result.exit_code == 0


async def test_process_order_create_auto_id(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test clive process order create with auto-calculated order_id."""
    # ARRANGE - don't specify order_id

    # ACT
    result = cli_tester.process_order_create(
        from_=WORKING_ACCOUNT_NAME,
        amount_to_sell=HIVE_AMOUNT,
        min_to_receive=HBD_AMOUNT,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert result.exit_code == 0


@pytest.mark.skip(
    reason="Cannot test custom expiration reliably - testnet head_block_time differs from wall-clock time"
)
async def test_process_order_create_custom_expiration(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process order create with custom expiration date."""
    # This test is skipped because the testnet's head_block_time is different from wall-clock time,
    # making it impossible to specify a valid custom expiration without querying the node first.
    _ = node, cli_tester


@pytest.mark.skip(
    reason="fill_or_kill requires a matching counter-order on the testnet which doesn't exist"
)
async def test_process_order_create_fill_or_kill(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process order create with fill_or_kill flag."""
    # This test is skipped because fill_or_kill=true requires an existing counter-order
    # on the market that can fill this order immediately. Without it, the order is cancelled
    # by the blockchain with "Cancelling order because it was not filled."
    _ = node, cli_tester


async def test_process_order_cancel(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process order cancel command."""
    # ARRANGE - first create an order
    order_id = 10

    cli_tester.process_order_create(
        from_=WORKING_ACCOUNT_NAME,
        amount_to_sell=HIVE_AMOUNT,
        min_to_receive=HBD_AMOUNT,
        order_id=order_id,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    expected_operation = LimitOrderCancelOperation(
        owner=WORKING_ACCOUNT_NAME,
        orderid=order_id,
    )

    # ACT
    result = cli_tester.process_order_cancel(
        from_=WORKING_ACCOUNT_NAME,
        order_id=order_id,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, expected_operation)


async def test_show_orders(
    node: tt.RawNode,  # noqa: ARG001
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
    # The output should contain the order table or order information
    output = result.output.lower()
    assert "order" in output or str(order_id) in result.output


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


async def test_process_order_create_same_asset_error(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test that order create fails when both assets are the same type."""
    # ARRANGE
    order_id = 30
    hive_sell = tt.Asset.Test(100)
    hive_receive = tt.Asset.Test(50)  # Same asset type as sell

    expected_error = get_formatted_error_message(OrderSameAssetError())

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_order_create(
            from_=WORKING_ACCOUNT_NAME,
            amount_to_sell=hive_sell,
            min_to_receive=hive_receive,
            order_id=order_id,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_process_order_create_past_expiration_error(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test that order create fails when expiration is in the past."""
    # ARRANGE - use a very old date that's always in the past relative to any head_block_time
    past_expiration = "2000-01-01T00:00:00"
    order_id = 31

    expected_error = get_formatted_error_message(
        OrderInvalidExpirationError("Expiration must be in the future.")
    )

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_order_create(
            from_=WORKING_ACCOUNT_NAME,
            amount_to_sell=HIVE_AMOUNT,
            min_to_receive=HBD_AMOUNT,
            order_id=order_id,
            expiration=past_expiration,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_process_order_create_both_min_and_price_error(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test that order create fails when both --min-to-receive and --price are specified."""
    # ARRANGE
    order_id = 32
    price = Decimal("0.25")

    expected_error = get_formatted_error_message(OrderMutuallyExclusiveOptionsError())

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_order_create(
            from_=WORKING_ACCOUNT_NAME,
            amount_to_sell=HIVE_AMOUNT,
            min_to_receive=HBD_AMOUNT,
            price=price,
            order_id=order_id,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_process_order_create_neither_min_nor_price_error(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test that order create fails when neither --min-to-receive nor --price is specified."""
    # ARRANGE
    order_id = 33

    expected_error = get_formatted_error_message(OrderMissingPriceSpecificationError())

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_order_create(
            from_=WORKING_ACCOUNT_NAME,
            amount_to_sell=HIVE_AMOUNT,
            order_id=order_id,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )
