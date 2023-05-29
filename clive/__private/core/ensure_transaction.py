from __future__ import annotations

from collections.abc import Iterable
from datetime import timedelta
from typing import TYPE_CHECKING, Any, TypeAlias

from clive.__private.core.commands.build_transaction import BuildTransaction
from clive.models import Operation, OperationBaseClass, Transaction

if TYPE_CHECKING:
    from clive.__private.core.node.node import Node

    TransactionConvertibleType: TypeAlias = Operation | Iterable[Operation] | Transaction


def ensure_transaction(
    content: TransactionConvertibleType, node: Node, expiration: timedelta = timedelta(minutes=30)
) -> Transaction:
    """Ensures that the given content is a transaction.

    If the content is a transaction, it is returned as-is.
    If the content is a list of operations, they are gathered into a transaction and returned.

    Args:
        content: The content to ensure is a transaction.

    Returns:
        The transaction.
    """

    def __ensure_operation(item: Any) -> Operation:
        assert isinstance(item, OperationBaseClass)
        return item  # type: ignore[return-value]

    if isinstance(content, Transaction):
        return content

    if isinstance(content, OperationBaseClass):
        operations = [content]

    elif isinstance(content, Iterable):
        operations = [__ensure_operation(x) for x in content]
    else:
        raise TypeError(f"Expected a transaction, operation or iterable of operations, got {type(content)}")

    return BuildTransaction(operations, node=node, expiration=expiration).execute_with_result()
