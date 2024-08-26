from __future__ import annotations

from clive.__private.cli.completion import is_tab_completion_active

if not is_tab_completion_active():
    from .aliased import (
        ApiOperationObject,
        ApiVirtualOperationObject,
        OperationBase,
        OperationRepresentationUnion,
        OperationUnion,
        Signature,
        VirtualOperationBaseClass,
        VirtualOperationRepresentationType,
        VirtualOperationUnion,
    )
    from .asset import Asset
    from .hp_vests_balance import HpVestsBalance
    from .transaction import Transaction, TransactionWithHash

    __all__ = [
        "ApiOperationObject",
        "ApiVirtualOperationObject",
        "Asset",
        "HpVestsBalance",
        "OperationBase",
        "OperationRepresentationUnion",
        "OperationUnion",
        "Signature",
        "Transaction",
        "TransactionWithHash",
        "VirtualOperationBaseClass",
        "VirtualOperationRepresentationType",
        "VirtualOperationRepresentationType",
        "VirtualOperationUnion",
    ]
