from __future__ import annotations

from clive.__private.cli.completion import is_tab_completion_active

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
    from .asset import Asset
    from .transaction import Transaction, TransactionWithHash
    from .transaction_convertible import TransactionConvertibleType

    __all__ = [
        "ApiOperationObject",
        "ApiVirtualOperationObject",
        "Operation",
        "OperationBaseClass",
        "OperationRepresentationType",
        "Signature",
        "TransactionConvertibleType",
        "VirtualOperation",
        "VirtualOperationBaseClass",
        "VirtualOperationRepresentationType",
        "VirtualOperationRepresentationType",
        "Asset",
        "Transaction",
        "TransactionWithHash",
    ]
