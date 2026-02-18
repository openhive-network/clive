from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import (
    OrderExpirationNotInFutureError,
    OrderExpirationTooFarInFutureError,
    OrderFillOrKillNotFilledError,
    OrderMissingPriceSpecificationError,
    OrderMutuallyExclusiveOptionsError,
    OrderSameAssetError,
)
from clive.__private.models.schemas import (
    HbdExchangeRate,
    HiveDateTime,
    LimitOrderCancelOperation,
    LimitOrderCreate2Operation,
    LimitOrderCreateOperation,
)
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import ALT_WORKING_ACCOUNT1_KEY_ALIAS, WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import get_formatted_error_message, get_transaction_id_from_output
from clive_local_tools.testnet_block_log.constants import (
    ALT_WORKING_ACCOUNT1_DATA,
    ALT_WORKING_ACCOUNT1_NAME,
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester
    from clive_local_tools.cli.result_wrapper import CLITestResult

HIVE_AMOUNT: Final[tt.Asset.TestT] = tt.Asset.Test(100)
HBD_AMOUNT: Final[tt.Asset.TbdT] = tt.Asset.Tbd(25)


def assert_limit_order_create2_in_blockchain(  # noqa: PLR0913
    node: tt.RawNode,
    result: CLITestResult,
    expected_owner: str,
    expected_order_id: int,
    expected_amount_to_sell: tt.Asset.AnyT,
    expected_exchange_rate: HbdExchangeRate,
    expected_expiration: str,
) -> None:
    """Verify LimitOrderCreate2Operation fields in blockchain.

    LimitOrderCreate2Operation contains a nested HbdExchangeRate that is not fully deserialized
    by the schemas library when reading from the blockchain (stays as dict), so standard equality
    comparison via assert_operations_placed_in_blockchain does not work. This helper checks fields
    individually.
    """
    transaction_id = get_transaction_id_from_output(result.stdout)
    node.wait_number_of_blocks(1)
    transaction = node.api.account_history.get_transaction(id_=transaction_id, include_reversible=True)

    for op_repr in transaction.operations:
        op = op_repr.value
        if not isinstance(op, LimitOrderCreate2Operation):
            continue

        assert op.owner == expected_owner
        assert op.orderid == expected_order_id
        assert op.amount_to_sell == expected_amount_to_sell
        assert op.fill_or_kill is False

        # exchange_rate is deserialized as dict from blockchain
        er = op.exchange_rate
        if isinstance(er, dict):
            assert er["base"] == expected_exchange_rate.base
            assert er["quote"] == expected_exchange_rate.quote
        else:
            assert er.base == expected_exchange_rate.base
            assert er.quote == expected_exchange_rate.quote

        assert str(op.expiration).replace("+00:00", "").replace(" ", "T") == expected_expiration
        return

    pytest.fail("LimitOrderCreate2Operation not found in transaction.")


def assert_order_on_chain_with_relative_expiration(
    node: tt.RawNode,
    account_name: str,
    order_id: int,
    expected_delta: timedelta,
    tolerance: timedelta = timedelta(seconds=30),
) -> None:
    """Verify order exists on chain and its expiration matches the expected relative delta from creation."""
    node.wait_number_of_blocks(1)
    orders = node.api.database_api.find_limit_orders(account=account_name)
    matching = [o for o in orders.orders if o.orderid == order_id]
    assert len(matching) == 1, f"Expected 1 order with id {order_id}, found {len(matching)}"
    order = matching[0]
    actual_delta = order.expiration - order.created
    assert abs(actual_delta - expected_delta) < tolerance, (
        f"Expected expiration delta ~{expected_delta}, got {actual_delta}"
    )


async def test_process_order_create_with_min_to_receive(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process order create with --min-to-receive option uses LimitOrderCreateOperation."""
    # ARRANGE
    order_id = 1
    dgpo = node.api.database_api.get_dynamic_global_properties()
    expiration = dgpo.time + timedelta(hours=1)
    expiration_str = expiration.strftime("%Y-%m-%dT%H:%M:%S")

    expected_operation = LimitOrderCreateOperation(
        owner=WORKING_ACCOUNT_NAME,
        orderid=order_id,
        amount_to_sell=HIVE_AMOUNT,
        min_to_receive=HBD_AMOUNT,
        fill_or_kill=False,
        expiration=HiveDateTime(expiration),
    )

    # ACT
    result = cli_tester.process_order_create(
        from_=WORKING_ACCOUNT_NAME,
        amount_to_sell=HIVE_AMOUNT,
        min_to_receive=HBD_AMOUNT,
        order_id=order_id,
        expiration=expiration_str,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, expected_operation)


async def test_process_order_create_with_price(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process order create with --price option uses LimitOrderCreate2Operation."""
    # ARRANGE
    order_id = 2
    price = Decimal("0.25")  # 0.250 TBD per TESTS
    dgpo = node.api.database_api.get_dynamic_global_properties()
    expiration = dgpo.time + timedelta(hours=1)
    expiration_str = expiration.strftime("%Y-%m-%dT%H:%M:%S")

    # When selling 100 HIVE at price 0.250 TBD/HIVE, exchange_rate base=100 HIVE, quote=25 TBD
    expected_exchange_rate = HbdExchangeRate(
        base=HIVE_AMOUNT,
        quote=tt.Asset.Tbd(25),
    )

    # ACT
    result = cli_tester.process_order_create(
        from_=WORKING_ACCOUNT_NAME,
        amount_to_sell=HIVE_AMOUNT,
        price=price,
        order_id=order_id,
        expiration=expiration_str,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_limit_order_create2_in_blockchain(
        node, result, WORKING_ACCOUNT_NAME, order_id, HIVE_AMOUNT, expected_exchange_rate, expiration_str
    )


async def test_process_order_create_sell_hbd(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test creating an order to sell HBD for HIVE."""
    # ARRANGE
    order_id = 4
    dgpo = node.api.database_api.get_dynamic_global_properties()
    expiration = dgpo.time + timedelta(hours=1)
    expiration_str = expiration.strftime("%Y-%m-%dT%H:%M:%S")

    expected_operation = LimitOrderCreateOperation(
        owner=WORKING_ACCOUNT_NAME,
        orderid=order_id,
        amount_to_sell=HBD_AMOUNT,
        min_to_receive=HIVE_AMOUNT,
        fill_or_kill=False,
        expiration=HiveDateTime(expiration),
    )

    # ACT
    result = cli_tester.process_order_create(
        from_=WORKING_ACCOUNT_NAME,
        amount_to_sell=HBD_AMOUNT,
        min_to_receive=HIVE_AMOUNT,
        order_id=order_id,
        expiration=expiration_str,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, expected_operation)


async def test_process_order_create_with_price_sell_hbd(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process order create with --price option when selling HBD."""
    # ARRANGE
    order_id = 70
    price = Decimal("0.25")  # 0.250 TBD per TESTS (1 HIVE = 0.25 HBD)
    dgpo = node.api.database_api.get_dynamic_global_properties()
    expiration = dgpo.time + timedelta(hours=1)
    expiration_str = expiration.strftime("%Y-%m-%dT%H:%M:%S")

    # When selling 25 HBD at price 0.250 TBD/TESTS, exchange_rate base=25 HBD, quote=100 HIVE
    expected_exchange_rate = HbdExchangeRate(
        base=HBD_AMOUNT,
        quote=tt.Asset.Test(100),
    )

    # ACT
    result = cli_tester.process_order_create(
        from_=WORKING_ACCOUNT_NAME,
        amount_to_sell=HBD_AMOUNT,  # 25 HBD
        price=price,
        order_id=order_id,
        expiration=expiration_str,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_limit_order_create2_in_blockchain(
        node, result, WORKING_ACCOUNT_NAME, order_id, HBD_AMOUNT, expected_exchange_rate, expiration_str
    )


async def test_process_order_create_auto_id(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process order create with auto-calculated order_id."""
    # ARRANGE - don't specify order_id, use --price (HBD/HIVE = 25/100 = 0.25)
    price = Decimal("0.25")

    # ACT
    result = cli_tester.process_order_create(
        from_=WORKING_ACCOUNT_NAME,
        amount_to_sell=HIVE_AMOUNT,
        price=price,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT - verify operation placed in blockchain
    transaction_id = get_transaction_id_from_output(result.stdout)
    node.wait_number_of_blocks(1)
    transaction = node.api.account_history.get_transaction(id_=transaction_id, include_reversible=True)
    assert any(isinstance(op.value, LimitOrderCreate2Operation) for op in transaction.operations)


async def test_process_order_create_custom_expiration(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process order create with absolute expiration date."""
    # ARRANGE
    order_id = 40
    dgpo = node.api.database_api.get_dynamic_global_properties()
    expiration = dgpo.time + timedelta(seconds=60)
    expiration_str = expiration.strftime("%Y-%m-%dT%H:%M:%S")

    # ACT
    cli_tester.process_order_create(
        from_=WORKING_ACCOUNT_NAME,
        amount_to_sell=HIVE_AMOUNT,
        min_to_receive=HBD_AMOUNT,
        order_id=order_id,
        expiration=expiration_str,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT - verify order is in blockchain with correct expiration (tolerance accounts for block production delay)
    assert_order_on_chain_with_relative_expiration(
        node, WORKING_ACCOUNT_NAME, order_id, expected_delta=timedelta(seconds=60)
    )


async def test_process_order_create_relative_expiration(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process order create with relative expiration like '+1d'."""
    # ARRANGE
    order_id = 41

    # ACT
    cli_tester.process_order_create(
        from_=WORKING_ACCOUNT_NAME,
        amount_to_sell=HIVE_AMOUNT,
        min_to_receive=HBD_AMOUNT,
        order_id=order_id,
        expiration="+1d",
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT - verify order is in blockchain with correct relative expiration
    assert_order_on_chain_with_relative_expiration(
        node, WORKING_ACCOUNT_NAME, order_id, expected_delta=timedelta(days=1)
    )


async def test_process_order_create_fill_or_kill(
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


async def test_process_order_create_same_asset_error(
    cli_tester: CLITester,
) -> None:
    """Test that order create fails when both assets are the same type (HIVE/HIVE)."""
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


async def test_process_order_create_same_asset_hbd_error(
    cli_tester: CLITester,
) -> None:
    """Test that order create fails when both assets are the same type (HBD/HBD)."""
    # ARRANGE
    order_id = 34
    hbd_sell = tt.Asset.Tbd(25)
    hbd_receive = tt.Asset.Tbd(50)  # Same asset type as sell

    expected_error = get_formatted_error_message(OrderSameAssetError())

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_order_create(
            from_=WORKING_ACCOUNT_NAME,
            amount_to_sell=hbd_sell,
            min_to_receive=hbd_receive,
            order_id=order_id,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_process_order_create_past_expiration_error(
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


async def test_process_order_create_too_far_future_expiration_error(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test that order create fails when expiration exceeds the maximum allowed 28 days."""
    # ARRANGE - compute an expiration 29 days after head_block_time (limit is 28 days)
    dgpo = node.api.database_api.get_dynamic_global_properties()
    too_far_expiration = dgpo.time + timedelta(days=29)
    expiration_str = too_far_expiration.strftime("%Y-%m-%dT%H:%M:%S")
    order_id = 35

    expected_error = get_formatted_error_message(OrderExpirationTooFarInFutureError())

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_order_create(
            from_=WORKING_ACCOUNT_NAME,
            amount_to_sell=HIVE_AMOUNT,
            min_to_receive=HBD_AMOUNT,
            order_id=order_id,
            expiration=expiration_str,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_process_order_create_both_min_and_price_error(
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
    cli_tester: CLITester,
) -> None:
    """Test that fill-or-kill order fails gracefully when no matching order exists (selling HIVE)."""
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


async def test_process_order_create_fill_or_kill_hbd_no_matching_order(
    cli_tester: CLITester,
) -> None:
    """Test that fill-or-kill order fails gracefully when no matching order exists (selling HBD)."""
    # ARRANGE - create fill_or_kill order selling HBD without any counter-order
    order_id = 53

    expected_error = get_formatted_error_message(OrderFillOrKillNotFilledError())

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_order_create(
            from_=WORKING_ACCOUNT_NAME,
            amount_to_sell=HBD_AMOUNT,
            min_to_receive=HIVE_AMOUNT,
            order_id=order_id,
            fill_or_kill=True,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )
