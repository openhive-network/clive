from __future__ import annotations

from typing import TYPE_CHECKING

import wax
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from clive.models.operation import Operation
    from clive.models.transaction import Transaction


class WaxOperationFailedError(CliveError):
    pass


def __validate_wax_response(response: wax.python_result) -> bool:
    if response.status == wax.python_error_code.fail:
        raise WaxOperationFailedError(response.exception_message.decode())
    return True


def validate_transaction(transaction: Transaction) -> bool:
    return __validate_wax_response(wax.validate_transaction(transaction.as_json().encode()))


def validate_operation(operation: Operation) -> bool:
    return __validate_wax_response(wax.validate_operation(operation.as_json().encode()))


def calculate_digest(transaction: Transaction, chain_id: str) -> str:
    result = wax.calculate_digest(transaction.as_json().encode(), chain_id.encode())
    __validate_wax_response(result)
    return result.result.decode()


def serialize_transaction(transaction: Transaction) -> bytes:
    result = wax.serialize_transaction(transaction.as_json().encode())
    __validate_wax_response(result)
    return result.result
