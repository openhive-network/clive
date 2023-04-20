from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, TypeAlias

from clive.models.operation import Operation
from clive.models.transaction import Transaction

if TYPE_CHECKING:
    TransactionConvertibleType: TypeAlias = Operation | Iterable[Operation] | Transaction


def ensure_transaction(content: TransactionConvertibleType) -> Transaction:
    """Ensures that the given content is a transaction.

    If the content is a transaction, it is returned as-is.
    If the content is a list of operations, they are gathered into a transaction and returned.

    Args:
        content: The content to ensure is a transaction.

    Returns:
        The transaction.
    """
    if isinstance(content, Transaction):
        return content
    if isinstance(content, Operation):
        return Transaction(content)
    if isinstance(content, Iterable):
        return Transaction(*content)
    raise TypeError(f"Expected a transaction, operation or iterable of operations, got {type(content)}")
