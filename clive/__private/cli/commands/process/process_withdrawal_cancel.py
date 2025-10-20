from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.schemas import CancelTransferFromSavingsOperation

if TYPE_CHECKING:
    from clive.__private.cli.types import ComposeTransaction


@dataclass(kw_only=True)
class ProcessWithdrawalCancel(OperationCommand):
    from_account: str
    request_id: int

    async def _create_operations(self) -> ComposeTransaction:
        yield CancelTransferFromSavingsOperation(
            from_=self.from_account,
            request_id=self.request_id,
        )
