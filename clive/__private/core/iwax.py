from __future__ import annotations

from typing import TYPE_CHECKING

import wax

if TYPE_CHECKING:
    from clive.models.operation import Operation
    from clive.models.transaction import Transaction


def validate_transaction(transaction: Transaction) -> bool | None:
    return wax.validate_transaction(serialize_transaction_to_bytes(transaction))  # type: ignore[no-any-return]


def validate_operation(operation: Operation) -> bool | None:
    return wax.validate_operation(operation.as_json().encode())  # type: ignore[no-any-return]


def calculate_digest(transaction: Transaction, chain_id: str) -> str:
    trx = serialize_transaction_to_bytes(transaction)
    result = wax.calculate_digest(trx, chain_id.encode())
    assert result is not None
    success, digest = result
    assert success is True
    return digest  # type: ignore[no-any-return]


def serialize_transaction(transaction: Transaction) -> str:
    return transaction.as_json(by_alias=True, exclude_none=True)


def serialize_transaction_to_bytes(transaction: Transaction) -> bytes:
    return serialize_transaction(transaction).encode()
