from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, TypeAlias

from clive.__private.core.commands.build_transaction import BuildTransaction
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

    command = None
    if isinstance(content, Operation):
    def __ensure_operation(item: Any) -> Operation:
        assert isinstance(item, Operation)
        return item
    
    if isinstance(content, Transaction):
        return content

    if isinstance(content, Operation):
        operations = [content]
    elif isinstance(content, Iterable):
        operations = [__ensure_operation(x) for x in content]
    else:
        raise TypeError(f"Expected a transaction, operation or iterable of operations, got {type(content)}")

    return execute_with_result(BuildTransaction(operations))
