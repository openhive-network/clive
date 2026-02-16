from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import (
    OrderExpirationNotInFutureError,
    OrderFillOrKillNotFilledError,
    OrderMissingPriceSpecificationError,
    OrderMutuallyExclusiveOptionsError,
    OrderSameAssetError,
)
from clive.__private.models.schemas import (
    LimitOrderCancelOperation,
    LimitOrderCreate2Operation,
    LimitOrderCreateOperation,
)
from clive_local_tools.checkers.blockchain_checkers import (
    assert_operation_type_in_blockchain,
    assert_operations_placed_in_blockchain,
)
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import ALT_WORKING_ACCOUNT1_KEY_ALIAS, WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import get_formatted_error_message
from clive_local_tools.testnet_block_log.constants import (
    ALT_WORKING_ACCOUNT1_DATA,
    ALT_WORKING_ACCOUNT1_NAME,
    WATCHED_ACCOUNTS_DATA,
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

HIVE_AMOUNT: Final[tt.Asset.TestT] = tt.Asset.Test(100)
HBD_AMOUNT: Final[tt.Asset.TbdT] = tt.Asset.Tbd(25)


async def test_process_order_create_with_min_to_receive(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process order create with --min-to-receive option uses LimitOrderCreateOperation."""
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
    assert_operation_type_in_blockchain(node, result, LimitOrderCreateOperation)


async def test_process_order_create_with_price(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process order create with --price option uses LimitOrderCreate2Operation."""
    # ARRANGE
    order_id = 2
    price = tt.Asset.Tbd(0.25)  # 0.250 TBD per TESTS

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
    assert_operation_type_in_blockchain(node, result, LimitOrderCreate2Operation)


async def test_process_order_create_with_price_sell_hbd(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process order create with --price option when selling HBD."""
    # ARRANGE
    order_id = 70
    price = tt.Asset.Tbd(4)  # 4.000 TBD per TBD

    # ACT
    result = cli_tester.process_order_create(
        from_=WORKING_ACCOUNT_NAME,
        amount_to_sell=HBD_AMOUNT,  # 25 HBD
        price=price,
        order_id=order_id,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert result.exit_code == 0
    assert_operation_type_in_blockchain(node, result, LimitOrderCreate2Operation)


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


async def test_process_order_create_custom_expiration(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process order create with custom expiration date."""
    # Get head_block_time from node
    dgpo = node.api.database_api.get_dynamic_global_properties()
    head_block_time = dgpo.time

    # Calculate expiration 1 hour after head_block_time
    future_expiration = head_block_time + timedelta(hours=1)
    expiration_str = future_expiration.strftime("%Y-%m-%dT%H:%M:%S")

    order_id = 40

    result = cli_tester.process_order_create(
        from_=WORKING_ACCOUNT_NAME,
        amount_to_sell=HIVE_AMOUNT,
        min_to_receive=HBD_AMOUNT,
        order_id=order_id,
        expiration=expiration_str,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    assert result.exit_code == 0


async def test_process_order_create_fill_or_kill(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test clive process order create with fill_or_kill flag."""
    # Add mary's key to the wallet so we can sign transactions for her
    cli_tester.configure_key_add(
        key=ALT_WORKING_ACCOUNT1_DATA.account.private_key,
        alias=ALT_WORKING_ACCOUNT1_KEY_ALIAS,
    )

    # First create a counter-order from mary selling HBD for HIVE
    counter_order_id = 50
    cli_tester.process_order_create(
        from_=ALT_WORKING_ACCOUNT1_NAME,
        amount_to_sell=HBD_AMOUNT,  # 25 HBD
        min_to_receive=HIVE_AMOUNT,  # 100 HIVE
        order_id=counter_order_id,
        sign_with=ALT_WORKING_ACCOUNT1_KEY_ALIAS,
    )

    # Now alice creates fill_or_kill order - should match immediately
    order_id = 51
    result = cli_tester.process_order_create(
        from_=WORKING_ACCOUNT_NAME,
        amount_to_sell=HIVE_AMOUNT,  # 100 HIVE
        min_to_receive=HBD_AMOUNT,  # 25 HBD
        order_id=order_id,
        fill_or_kill=True,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    assert result.exit_code == 0


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
    output = result.output.lower()

    # Check that the table contains expected column headers
    assert "original" in output
    assert "for" in output
    assert "remaining" in output
    assert "for (rem)" in output

    # Check that order values are displayed (100.000 TESTS and 25.000 TBD)
    # Since the order wasn't partially filled, Original and Remaining should be equal
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

    expected_error = get_formatted_error_message(OrderExpirationNotInFutureError())

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
    price = tt.Asset.Tbd(0.25)

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


async def test_process_order_create_fill_or_kill_no_matching_order(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test that fill-or-kill order fails gracefully when no matching order exists."""
    # ARRANGE - create fill_or_kill order without any counter-order
    order_id = 52

    expected_error = get_formatted_error_message(OrderFillOrKillNotFilledError())

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_order_create(
            from_=WORKING_ACCOUNT_NAME,
            amount_to_sell=HIVE_AMOUNT,
            min_to_receive=HBD_AMOUNT,
            order_id=order_id,
            fill_or_kill=True,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )
