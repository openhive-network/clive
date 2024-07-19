from __future__ import annotations

from typing import TYPE_CHECKING

from click.testing import Result

from clive_local_tools.cli.helpers import get_transaction_id_from_result

if TYPE_CHECKING:
    import test_tools as tt

    from schemas.operations import AnyOperation
    from schemas.operations.representations import HF26Representation


def _ensure_transaction_id(trx_id_or_result: Result | str) -> str:
    if isinstance(trx_id_or_result, Result):
        return get_transaction_id_from_result(trx_id_or_result)
    return trx_id_or_result


def assert_transaction_in_blockchain(
    node: tt.RawNode, trx_id_or_result: str | Result, *, wait_for_the_next_block: bool = True
) -> None:
    transaction_id = _ensure_transaction_id(trx_id_or_result)
    if wait_for_the_next_block:
        # Wait for transaction be available in block
        node.wait_number_of_blocks(1)
    node.api.account_history.get_transaction(
        id_=transaction_id,
        include_reversible=True,
    )


def assert_operations_placed_in_blockchain(
    node: tt.RawNode,
    trx_id_or_result: str | Result,
    *expected_operations: AnyOperation,
    wait_for_the_next_block: bool = True,
) -> None:
    assert_transaction_in_blockchain(node, trx_id_or_result, wait_for_the_next_block=wait_for_the_next_block)
    transaction_id = _ensure_transaction_id(trx_id_or_result)
    transaction = node.api.account_history.get_transaction(
        id=transaction_id,
        include_reversible=True,  # type: ignore[call-arg] # TODO: id -> id_ after helpy bug fixed
    )
    operations_to_check = list(expected_operations)
    for operation_representation in transaction.operations:
        _operation_representation: HF26Representation[AnyOperation] = operation_representation
        operation = _operation_representation.value
        if operation in operations_to_check:
            operations_to_check.remove(operation)

    message = (
        "Operations missing in blockchain.\n"
        f"Operations: {operations_to_check}\n"
        "were not found in the transaction:\n"
        f"{transaction}."
    )
    assert not operations_to_check, message
