from __future__ import annotations

from typing import TYPE_CHECKING

import wax
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from clive.models import Operation, Transaction


class WaxOperationFailedError(CliveError):
    pass


def __validate_wax_response(response: wax.python_result) -> bool:
    if response.status == wax.python_error_code.fail:
        raise WaxOperationFailedError(response.exception_message.decode())
    return True


def __as_binary_json(item: Operation | Transaction) -> bytes:
    return item.json(by_alias=True).encode()


def validate_transaction(transaction: Transaction) -> bool:
    return __validate_wax_response(wax.validate_transaction(__as_binary_json(transaction)))


def validate_operation(operation: Operation) -> bool:
    return __validate_wax_response(wax.validate_operation(__as_binary_json(operation)))


def calculate_digest(transaction: Transaction, chain_id: str) -> str:
    result = wax.calculate_digest(__as_binary_json(transaction), chain_id.encode())
    __validate_wax_response(result)
    return result.result.decode()


def serialize_transaction(transaction: Transaction) -> bytes:
    result = wax.serialize_transaction(__as_binary_json(transaction))
    __validate_wax_response(result)
    return result.result
