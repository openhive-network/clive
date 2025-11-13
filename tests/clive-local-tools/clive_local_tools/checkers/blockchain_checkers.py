from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import beekeepy.exceptions as bke
import pytest
import test_tools as tt
from click.testing import Result

from clive.__private.core.percent_conversions import percent_to_hive_percent
from clive_local_tools.helpers import get_transaction_id_from_output

if TYPE_CHECKING:
    from clive.__private.models.asset import Asset
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


def assert_transaction_in_blockchain(
    node: tt.RawNode, trx_id_or_result: str | Result, *, wait_for_the_next_block: bool = True
) -> None:
    transaction_id = _ensure_transaction_id(trx_id_or_result)
    if wait_for_the_next_block:
        # Wait for transaction be available in block
        node.wait_number_of_blocks(1)
    try:
        node.api.account_history.get_transaction(id_=transaction_id, include_reversible=True)
    except bke.ErrorInResponseError:
        pytest.fail(f"The transaction with {transaction_id=} couldn't be found in the blockchain.")


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
    property_name: str, property_value: str | int | Decimal | Asset.LiquidT, witness: Witness
) -> None:
    """Assert that given proparty has expected value in the witness object obtained by api call to blockchain."""
    message = f"Witness property '{property_name}' does not have expected value."

    match property_name:
        case "account_creation_fee":
            assert witness.props.account_creation_fee is not None  #  https://gitlab.syncad.com/hive/schemas/-/issues/46
            assert witness.props.account_creation_fee == property_value, (
                f"{message} Expected: {property_value}, actual: {witness.props.account_creation_fee}"
            )
        case "maximum_block_size":
            assert witness.props.maximum_block_size == property_value, (
                f"{message} Expected: {property_value}, actual: {witness.props.maximum_block_size}"
            )
        case "hbd_interest_rate":
            assert isinstance(property_value, Decimal), "For hbd_interest_rate property_value must be Decimal."
            expected_api_value = percent_to_hive_percent(property_value)
            assert witness.props.hbd_interest_rate == expected_api_value, (
                f"{message} Expected: {expected_api_value}, actual: {witness.props.hbd_interest_rate}"
            )
        case "new_signing_key":
            assert witness.signing_key == property_value, (
                f"{message} Expected: {property_value}, actual: {witness.signing_key}"
            )
        case "hbd_exchange_rate":
            assert witness.hbd_exchange_rate.base == property_value, (
                f"{message} Expected base: {property_value}, actual base: {witness.hbd_exchange_rate.quote}"
            )
            expected_quote = tt.Asset.Hive(1)
            assert witness.hbd_exchange_rate.quote == expected_quote, (
                f"{message} Expected quote: {expected_quote}, actual quote: {witness.hbd_exchange_rate.base}"
            )
        case "url":
            assert witness.url == property_value, f"{message} Expected: {property_value}, actual: {witness.url}"
        case "account_subsidy_budget":
            assert witness.props.account_subsidy_budget == property_value, (
                f"{message} Expected: {property_value}, actual: {witness.props.account_subsidy_budget}"
            )
        case "account_subsidy_decay":
            assert witness.props.account_subsidy_decay == property_value, (
                f"{message} Expected: {property_value}, actual: {witness.props.account_subsidy_decay}"
            )
        case _:
            pytest.fail(f"Unknown property: '{property_name}'.")
