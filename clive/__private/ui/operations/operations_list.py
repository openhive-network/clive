"""File with available operations and matching buttons."""
from __future__ import annotations

from typing import TYPE_CHECKING, Final

from clive.__private.ui.operations import (
    Governance,
    Savings,
    TransferToAccount,
)

if TYPE_CHECKING:
    from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen


MAJOR_OPERATIONS: Final[list[type[OperationBaseScreen]]] = [TransferToAccount, Savings, Governance]
