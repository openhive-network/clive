from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from beekeepy.exceptions import ErrorInResponseError
from click.testing import Result

from clive_local_tools.helpers import get_transaction_id_from_output

if TYPE_CHECKING:
    import test_tools as tt

    from clive.__private.models.schemas import OperationUnion, TransactionInBlockchain


def _ensure_transaction_id(trx_id_or_result: Result | str) -> str:
    if isinstance(trx_id_or_result, Result):
        return get_transaction_id_from_output(trx_id_or_result.stdout)
    return trx_id_or_result


def assert_transaction_in_blockchain(
    node: tt.RawNode, trx_id_or_result: str | Result, *, wait_for_the_next_block: bool = True
) -> None:
    transaction_id = _ensure_transaction_id(trx_id_or_result)
    if wait_for_the_next_block:
        # Wait for transaction be available in block
        node.wait_number_of_blocks(1)
    try:
        node.api.account_history.get_transaction(id_=transaction_id, include_reversible=True)
    except ErrorInResponseError:
        pytest.fail(f"The transaction with {transaction_id=} couldn't be found in the blockchain.")


def assert_operations_placed_in_blockchain(
    node: tt.RawNode,
    trx_id_or_result: str | Result,
    *expected_operations: OperationUnion,
    wait_for_the_next_block: bool = True,
) -> None:
    assert_transaction_in_blockchain(node, trx_id_or_result, wait_for_the_next_block=wait_for_the_next_block)
    transaction_id = _ensure_transaction_id(trx_id_or_result)
    transaction: TransactionInBlockchain = node.api.account_history.get_transaction(
        id=transaction_id,
        include_reversible=True,  # type: ignore[call-arg] # TODO: id -> id_ after helpy bug fixed
    )
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
