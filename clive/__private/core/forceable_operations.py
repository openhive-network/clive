from __future__ import annotations

from typing import Final

from clive.__private.models.schemas import (
    DelegateVestingSharesOperation,
    RecurrentTransferOperation,
    SetWithdrawVestingRouteOperation,
    TransferFromSavingsOperation,
    TransferToSavingsOperation,
    TransferToVestingOperation,
)

FORCEABLE_OPERATIONS: Final[list[str]] = [
    TransferToSavingsOperation.get_name(),
    TransferToSavingsOperation.get_name_with_suffix(),
    TransferFromSavingsOperation.get_name(),
    TransferFromSavingsOperation.get_name_with_suffix(),
    RecurrentTransferOperation.get_name(),
    RecurrentTransferOperation.get_name_with_suffix(),
    DelegateVestingSharesOperation.get_name(),
    DelegateVestingSharesOperation.get_name_with_suffix(),
    TransferToVestingOperation.get_name(),
    TransferToVestingOperation.get_name_with_suffix(),
    SetWithdrawVestingRouteOperation.get_name(),
    SetWithdrawVestingRouteOperation.get_name_with_suffix(),
]


def is_forceable_operation(operation: str) -> bool:
    """Check if the operation is forceable."""
    return operation in FORCEABLE_OPERATIONS
