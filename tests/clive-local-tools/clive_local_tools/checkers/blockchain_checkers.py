from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import beekeepy.exceptions as bke
import pytest
from click.testing import Result

from clive.__private.core.percent_conversions import percent_to_hive_percent
from clive.__private.models.asset import Asset
from clive.__private.models.schemas import HbdExchangeRate
from clive_local_tools.helpers import get_transaction_id_from_output

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    import test_tools as tt

    from clive.__private.models.schemas import GetTransaction, OperationBase, OperationUnion, Witness


def _ensure_transaction_id(trx_id_or_result: Result | str) -> str:
    if isinstance(trx_id_or_result, Result):
        return get_transaction_id_from_output(trx_id_or_result.stdout)
    return trx_id_or_result


def _get_transaction(
    node: tt.RawNode, trx_id_or_result: str | Result, *, wait_for_the_next_block: bool
) -> GetTransaction:
    assert_transaction_in_blockchain(node, trx_id_or_result, wait_for_the_next_block=wait_for_the_next_block)
    transaction_id = _ensure_transaction_id(trx_id_or_result)
    return node.api.account_history.get_transaction(
        id=transaction_id,
        include_reversible=True,  # type: ignore[call-arg] # TODO: id -> id_ after helpy bug fixed
    )


def _is_transaction_in_blockchain(
    node: tt.RawNode, trx_id_or_result: str | Result, *, wait_for_the_next_block: bool = True
) -> bool:
    """Return True if transaction is found in the blockchain, False otherwise."""
    transaction_id = _ensure_transaction_id(trx_id_or_result)
    if wait_for_the_next_block:
        # Wait for transaction be available in block
        node.wait_number_of_blocks(1)

    try:
        node.api.account_history.get_transaction(id_=transaction_id, include_reversible=True)
    except bke.ErrorInResponseError:
        return False
    return True


def assert_transaction_in_blockchain(
    node: tt.RawNode, trx_id_or_result: str | Result, *, wait_for_the_next_block: bool = True
) -> None:
    if not _is_transaction_in_blockchain(node, trx_id_or_result, wait_for_the_next_block=wait_for_the_next_block):
        transaction_id = _ensure_transaction_id(trx_id_or_result)
        pytest.fail(f"The transaction with {transaction_id=} couldn't be found in the blockchain.")


def assert_transaction_not_in_blockchain(
    node: tt.RawNode, trx_id_or_result: str | Result, *, wait_for_the_next_block: bool = True
) -> None:
    if _is_transaction_in_blockchain(node, trx_id_or_result, wait_for_the_next_block=wait_for_the_next_block):
        transaction_id = _ensure_transaction_id(trx_id_or_result)
        pytest.fail(f"The transaction with {transaction_id=} was unexpectedly found in the blockchain.")


def assert_operations_placed_in_blockchain(
    node: tt.RawNode,
    trx_id_or_result: str | Result,
    *expected_operations: OperationUnion,
    wait_for_the_next_block: bool = True,
) -> None:
    transaction = _get_transaction(node, trx_id_or_result, wait_for_the_next_block=wait_for_the_next_block)
    operations_to_check = list(expected_operations)

    for operation_representation in transaction.operations:
        operation = operation_representation.value
        if operation in operations_to_check:
            operations_to_check.remove(operation)

    message = (
        "Operations missing in blockchain.\n"
        f"Operations: {operations_to_check}\n"
        "were not found in the transaction:\n"
        f"{transaction}."
    )
    assert not operations_to_check, message


def assert_operation_type_in_blockchain(
    node: tt.RawNode,
    trx_id_or_result: str | Result,
    *expected_types: type[OperationBase],
    wait_for_the_next_block: bool = True,
) -> None:
    transaction = _get_transaction(node, trx_id_or_result, wait_for_the_next_block=wait_for_the_next_block)
    types_to_check = list(expected_types)

    for operation_representation in transaction.operations:
        operation_type = type(operation_representation.value)
        if operation_type in types_to_check:
            types_to_check.remove(operation_type)

    message = (
        "Operation types missing in blockchain.\n"
        f"Types: {types_to_check}\n"
        "were not found in the transaction:\n"
        f"{transaction}."
    )
    assert not types_to_check, message


def assert_witness_property(
    property_name: str, property_value: str | int | Decimal | Asset.LiquidT | HbdExchangeRate, witness: Witness
) -> None:
    """Assert that given property has expected value in the witness object obtained by api call to blockchain."""
    props = witness.props

    def check(actual: Any, expected: Any) -> None:  # noqa: ANN401
        message = (
            f"Witness property '{property_name}' does not have expected value. Expected: {expected}, actual: {actual}"
        )
        assert actual == expected, message

    # Define specialized check functions
    def check_account_creation_fee() -> None:
        assert props.account_creation_fee is not None, "account_creation_fee is None (see issue #46)"
        check(props.account_creation_fee, property_value)

    def check_hbd_exchange_rate() -> None:
        if isinstance(property_value, HbdExchangeRate):
            hbd_exchange_rate = property_value
        elif isinstance(property_value, Asset.LiquidT):
            hbd_exchange_rate = HbdExchangeRate(base=property_value, quote=Asset.hive(1))
        else:
            pytest.fail(f"Unknown property_value type: {type(property_value)}")
        check(witness.hbd_exchange_rate.base, hbd_exchange_rate.base)
        check(witness.hbd_exchange_rate.quote, hbd_exchange_rate.quote)

    def check_hbd_interest_rate() -> None:
        assert isinstance(property_value, Decimal), "For hbd_interest_rate, property_value must be Decimal."
        expected = percent_to_hive_percent(property_value)
        check(props.hbd_interest_rate, expected)

    # Map of property_name → checker function
    check_map: dict[str, Callable[[], None]] = {
        "account_creation_fee": check_account_creation_fee,
        "account_subsidy_budget": lambda: check(props.account_subsidy_budget, property_value),
        "account_subsidy_decay": lambda: check(props.account_subsidy_decay, property_value),
        "hbd_exchange_rate": check_hbd_exchange_rate,
        "hbd_interest_rate": check_hbd_interest_rate,
        "maximum_block_size": lambda: check(props.maximum_block_size, property_value),
        "new_signing_key": lambda: check(witness.signing_key, property_value),
        "url": lambda: check(witness.url, property_value),
    }

    # Dispatch or fail if unknown property
    if property_name not in check_map:
        pytest.fail(f"Unknown property: '{property_name}'.")

    check_map[property_name]()
