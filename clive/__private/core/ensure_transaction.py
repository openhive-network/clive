from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from clive.__private.models import Transaction
from clive.__private.models.schemas import OperationBase, convert_to_representation

type TransactionConvertibleType = OperationBase | Iterable[OperationBase] | Transaction


def ensure_transaction(content: TransactionConvertibleType) -> Transaction:
    """
    Ensure that the given content is a transaction.

    If the content is a transaction, it is returned as-is.
    If the content is a list of operations, they are gathered into a transaction and returned.

    Args:
        content: The content to ensure is a transaction.

    Raises:
        TypeError: If the given value has an unsupported type.

    Returns:
        The transaction.
    """

    def __ensure_operation(item: Any) -> OperationBase:  # noqa: ANN401
        assert isinstance(item, OperationBase)
        return item

    if isinstance(content, Transaction):
        return content
    if isinstance(content, OperationBase):
        operations = [convert_to_representation(content)]
    elif isinstance(content, Iterable):
        operations = [convert_to_representation(__ensure_operation(x)) for x in content]
    else:
        raise TypeError(f"Expected a transaction, operation or iterable of operations, got {type(content)}")
    return Transaction(operations=operations)
