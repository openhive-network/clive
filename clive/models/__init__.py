from __future__ import annotations

from clive.__private.cli.completion import is_tab_completion_active

from .asset import Asset

__all__ = [
    "Asset",
]

if not is_tab_completion_active():
    from .aliased import (
        ApiOperationObject,
        ApiVirtualOperationObject,
        Operation,
        OperationBaseClass,
        OperationRepresentationType,
        Signature,
        VirtualOperation,
        VirtualOperationBaseClass,
        VirtualOperationRepresentationType,
    )
    from .transaction import Transaction, TransactionWithHash

    __all__ = [
        "ApiOperationObject",
        "ApiVirtualOperationObject",
        "Operation",
        "OperationBaseClass",
        "OperationRepresentationType",
        "Signature",
        "VirtualOperation",
        "VirtualOperationBaseClass",
        "VirtualOperationRepresentationType",
        "VirtualOperationRepresentationType",
        "Asset",
        "Transaction",
        "TransactionWithHash",
    ]
